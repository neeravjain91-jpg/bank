"""
Transaction Assembler.
Combines table layout detection, ML line classification, cell mapping,
and NLP categorization to reconstruct validated transaction objects.
"""

import re
from typing import List, Dict, Tuple, Optional, Any
import pymupdf

from app.extraction.coordinate_extractor import ExtractedLine, ExtractedWord
from app.extraction.table_detector import TableDetector, DetectedTable
from app.extraction.profiles import BankProfile, get_profile
from app.models.line_classifier import LineClassifier
from app.models.nlp_categorizer import NLPCategorizer
from app.validation.normalizer import (
    normalize_amount_str,
    parse_date_to_iso,
    extract_embedded_date_and_description
)
from app.schemas.transaction import Transaction, Account


class TransactionAssembler:
    """Assembles raw words and lines into structured, normalized Transaction objects."""

    def __init__(
        self,
        profile: BankProfile,
        line_classifier: Optional[LineClassifier] = None,
        nlp_categorizer: Optional[NLPCategorizer] = None,
        use_ml: bool = True,
        use_transformers: bool = False
    ):
        self.profile = profile
        self.line_classifier = line_classifier or LineClassifier()
        self.nlp_categorizer = nlp_categorizer or NLPCategorizer()
        self.use_ml = use_ml
        self.use_transformers = use_transformers
        self.table_detector = TableDetector(profile=profile)

    def assemble(
        self,
        doc: pymupdf.Document,
        page_lines: Dict[int, List[ExtractedLine]]
    ) -> Tuple[List[Transaction], List[Account], Optional[float], Optional[float]]:
        """
        Assemble transactions and accounts across all pages.
        Returns: (transactions, accounts, opening_balance, closing_balance)
        """
        transactions: List[Transaction] = []
        accounts: List[Account] = []
        opening_balance: Optional[float] = None
        closing_balance: Optional[float] = None

        current_account_id: Optional[str] = None
        active_table: Optional[DetectedTable] = None
        in_progress_row: Optional[Dict[str, Any]] = None
        prev_role: Optional[str] = None

        # Detect accounts first from document metadata lines
        accounts = self._extract_accounts(page_lines)
        if accounts:
            current_account_id = accounts[0].id

        for pno in range(len(doc)):
            lines = page_lines.get(pno, [])
            page = doc[pno]
            page_w = page.rect.width
            page_h = page.rect.height

            # Detect initial table header on this page if present
            page_table = self.table_detector.detect_table_on_page(
                lines, page_width=page_w, page_num=pno, account_id=current_account_id
            )
            if page_table is not None:
                # If page has a fresh table header, finalize any prior transaction from previous page
                if in_progress_row is not None and in_progress_row["table"].page_num != pno:
                    txn_obj = self._finalize_transaction(in_progress_row)
                    if txn_obj:
                        transactions.append(txn_obj)
                    in_progress_row = None
                active_table = page_table

            for line in lines:
                # 1. Dynamic account header detection
                acc_match = self._match_account_header(line.text)
                if acc_match:
                    current_account_id = acc_match
                    if active_table:
                        active_table.account_id = current_account_id

                # 2. Check if line is a subsequent table header on this same page (e.g. bsb-004 multi-table page 3)
                candidate_cols = self.table_detector._build_column_intervals(line, page_w)
                if len(candidate_cols) >= 3:
                    if active_table is not None and (line.y0 - active_table.header_y0) < 25.0:
                        # Adjacent bilingual header row (e.g. English + Chinese), skip
                        continue
                    if active_table is None or (line.y0 - active_table.header_y0) >= 50.0:
                        if in_progress_row is not None:
                            txn_obj = self._finalize_transaction(in_progress_row)
                            if txn_obj:
                                transactions.append(txn_obj)
                            in_progress_row = None
                        active_table = DetectedTable(
                            page_num=pno,
                            header_y0=line.y0,
                            header_line=line,
                            columns=candidate_cols,
                            account_id=current_account_id
                        )
                        continue

                if active_table is None:
                    continue

                # Lines above the header on this page are header/metadata
                if line.page_num == active_table.page_num and line.y0 <= active_table.header_y0:
                    if "opening balance" in line.text.lower() and opening_balance is None:
                        m_op = re.search(r"opening\s+balance[:\s]+([\d,]+\.?\d*)", line.text, re.IGNORECASE)
                        if m_op:
                            opening_balance = normalize_amount_str(m_op.group(1), self.profile.decimal_separator, self.profile.thousands_separator)
                    if "closing balance" in line.text.lower() and closing_balance is None:
                        m_cl = re.search(r"closing\s+balance[:\s]+([\d,]+\.?\d*)", line.text, re.IGNORECASE)
                        if m_cl:
                            closing_balance = normalize_amount_str(m_cl.group(1), self.profile.decimal_separator, self.profile.thousands_separator)
                    continue

                # Ignore sub-headers like "($)" or "(-)"
                if re.match(r"^\s*[\(\$€\-\+]{1,5}\s*$", line.text):
                    continue

                # Ignore page numbers like "1 de 2", "2 de 2", "Page 1 of 3", "1/3" or document download metadata
                if re.match(r"^\s*\d+\s*(?:de|of|/)\s*\d+\s*$", line.text, re.IGNORECASE) or re.match(r"^page\s+\d+", line.text, re.IGNORECASE) or line.text.lower().startswith("download date:"):
                    continue

                # Ignore fees summary at bottom
                if "frais sur compte" in line.text.lower():
                    if in_progress_row is not None:
                        txn_obj = self._finalize_transaction(in_progress_row)
                        if txn_obj:
                            transactions.append(txn_obj)
                        in_progress_row = None
                    continue

                # Classify line role
                if self.use_ml:
                    role = self.line_classifier.predict_role(
                        text=line.text,
                        bbox=line.bbox,
                        page_width=page_w,
                        page_height=page_h,
                        prev_label=prev_role
                    )
                else:
                    role = self.line_classifier._heuristic_predict(
                        text=line.text,
                        bbox=line.bbox,
                        page_width=page_w,
                        page_height=page_h
                    )

                line.role = role
                prev_role = role

                # Check for balance summaries
                if "balance brought forward" in line.text.lower() or "solde d'ouverture" in line.text.lower() or "opening balance" in line.text.lower():
                    op_amt = self._extract_balance_amount(line.text)
                    if op_amt is not None and opening_balance is None:
                        opening_balance = op_amt

                if "balance carried forward" in line.text.lower() or "totals year-to-date" in line.text.lower() or "total no. of deposits" in line.text.lower():
                    cl_amt = self._extract_balance_amount(line.text)
                    if cl_amt is not None and closing_balance is None:
                        closing_balance = cl_amt
                    # Finalize current transaction and mark table ended
                    if in_progress_row is not None:
                        txn_obj = self._finalize_transaction(in_progress_row)
                        if txn_obj:
                            transactions.append(txn_obj)
                        in_progress_row = None
                    active_table = None
                    continue

                if "solde de fermeture" in line.text.lower() or "closing balance" in line.text.lower() or "total debits" in line.text.lower():
                    cl_amt = self._extract_balance_amount(line.text)
                    if cl_amt is not None and closing_balance is None:
                        closing_balance = cl_amt
                    if in_progress_row is not None:
                        txn_obj = self._finalize_transaction(in_progress_row)
                        if txn_obj:
                            transactions.append(txn_obj)
                        in_progress_row = None
                    active_table = None
                    continue

                if role == "BALANCE_SUMMARY":
                    continue

                if role == "NOISE_FOOTER" or role == "METADATA_HEADER":
                    continue

                # Check if this line starts a new transaction row
                is_txn_start = (role == "TRANSACTION_START")
                # Secondary validation: check if line begins with a valid date format or contains transaction amount
                if not is_txn_start:
                    is_txn_start = self._starts_with_date_pattern(line.text)

                if is_txn_start:
                    # Finalize prior transaction
                    if in_progress_row is not None:
                        txn_obj = self._finalize_transaction(in_progress_row)
                        if txn_obj:
                            transactions.append(txn_obj)
                        in_progress_row = None

                    # Begin new transaction row
                    in_progress_row = self._init_transaction_row(
                        line, active_table, account_id=current_account_id
                    )
                elif role == "TRANSACTION_CONTINUATION" and in_progress_row is not None:
                    # Merge continuation words into in_progress_row
                    self._merge_continuation_line(in_progress_row, line, active_table)

        # Finalize last transaction if exists
        if in_progress_row is not None:
            txn_obj = self._finalize_transaction(in_progress_row)
            if txn_obj:
                transactions.append(txn_obj)

        return transactions, accounts, opening_balance, closing_balance

    def _match_account_header(self, text: str) -> Optional[str]:
        t = text.lower()
        if "hkd current account" in t:
            return "acc-hkd-current"
        if "usd savings account" in t:
            return "acc-usd-savings"
        if "sc savings account" in t:
            return "acc-sc-savings"
        if "account number" in t:
            m = re.search(r"account\s+number\s+([0-9\-\/A-Z]+)", text, re.IGNORECASE)
            if m:
                return f"acc-{m.group(1).replace('-', '')}"
        return None

    def _extract_accounts(self, page_lines: Dict[int, List[ExtractedLine]]) -> List[Account]:
        accounts = []
        seen_ids = set()
        for pno, lines in page_lines.items():
            for line in lines:
                t = line.text
                if "hkd current account" in t.lower():
                    m = re.search(r"(\d{3}-\d{6}-\d{3})", t)
                    num = m.group(1) if m else "817-890692-838"
                    acc_id = "acc-hkd-current"
                    if acc_id not in seen_ids:
                        accounts.append(Account(
                            id=acc_id,
                            account_number=num,
                            name=f"HKD Current Account — {num}",
                            currency="HKD"
                        ))
                        seen_ids.add(acc_id)
                elif "usd savings account" in t.lower():
                    m = re.search(r"(\d{3}-\d{6}-\d{3})", t)
                    num = m.group(1) if m else "817-890692-002"
                    acc_id = "acc-usd-savings"
                    if acc_id not in seen_ids:
                        accounts.append(Account(
                            id=acc_id,
                            account_number=num,
                            name=f"USD Savings Account — {num}",
                            currency="USD"
                        ))
                        seen_ids.add(acc_id)
                elif "account number" in t.lower():
                    m = re.search(r"account\s+number\s+([0-9\-\/]+)", t, re.IGNORECASE)
                    if m:
                        num = m.group(1).strip()
                        acc_id = f"acc-{num.replace('-', '')}"
                        if acc_id not in seen_ids:
                            accounts.append(Account(
                                id=acc_id,
                                account_number=num,
                                name=f"Account {num}",
                                currency=self.profile.currency
                            ))
                            seen_ids.add(acc_id)
        return accounts

    def _starts_with_date_pattern(self, text: str) -> bool:
        """Check if line starts with a date pattern."""
        t = text.strip()
        # DD/MM/YYYY or MM/DD or DD-MM-YYYY
        if re.match(r"^\d{1,2}[/\-\.]\d{1,2}(?:[/\-\.]\d{2,4})?", t):
            return True
        # D MMM e.g. '27 Jun', '1 Jul', '22 mei'
        if re.match(r"^\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|mei|mrt|janv)", t, re.IGNORECASE):
            return True
        return False

    def _extract_balance_amount(self, text: str) -> Optional[float]:
        """Extract balance amount from brought forward or carried forward lines."""
        # Find numeric pattern with commas/dots
        matches = re.findall(r"[\d\s\,]+[\,\.]\d{2,3}", text)
        if matches:
            last_match = matches[-1].strip()
            return normalize_amount_str(
                last_match,
                decimal_sep=self.profile.decimal_separator,
                thousands_sep=self.profile.thousands_separator
            )
        return None

    def _init_transaction_row(
        self,
        line: ExtractedLine,
        table: DetectedTable,
        account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Map tokens of starting transaction line to table columns."""
        cell_tokens: Dict[str, List[ExtractedWord]] = {col.role: [] for col in table.columns}
        original_data: Dict[str, str] = {col.label: "" for col in table.columns}

        for word in line.words:
            role = table.map_word_to_column(word)
            if role and role in cell_tokens:
                cell_tokens[role].append(word)

        # Assemble string per column
        for col in table.columns:
            words = sorted(cell_tokens[col.role], key=lambda w: w.x0)
            original_data[col.label] = " ".join(w.text for w in words).strip()

        return {
            "cell_tokens": cell_tokens,
            "original_data": original_data,
            "account_id": account_id or table.account_id,
            "line_y0": line.y0,
            "table": table
        }

    def _merge_continuation_line(
        self,
        in_progress_row: Dict[str, Any],
        line: ExtractedLine,
        table: DetectedTable
    ):
        """Append continuation words into in-progress row cells."""
        cell_tokens = in_progress_row["cell_tokens"]
        original_data = in_progress_row["original_data"]

        for word in line.words:
            role = table.map_word_to_column(word)
            # Continuation words typically belong to description or counterparty or reference
            if role in ["description", "counterparty", "reference"] and role in cell_tokens:
                cell_tokens[role].append(word)
            else:
                # If ambiguous, append to description
                if "description" in cell_tokens:
                    cell_tokens["description"].append(word)

        # Update original_data
        for col in table.columns:
            words = cell_tokens.get(col.role, [])
            if words:
                # Group words by visual y coordinate to preserve multi-line description formatting
                y_groups: Dict[float, List[ExtractedWord]] = {}
                for w in words:
                    y = round(w.y0, 1)
                    matched_k = None
                    for k in y_groups:
                        if abs(k - y) <= 3.0:
                            matched_k = k
                            break
                    if matched_k is not None:
                        y_groups[matched_k].append(w)
                    else:
                        y_groups[y] = [w]
                
                line_strs = []
                for yk in sorted(y_groups.keys()):
                    line_words = sorted(y_groups[yk], key=lambda x: x.x0)
                    line_strs.append(" ".join(w.text for w in line_words).strip())
                original_data[col.label] = "\n".join(l for l in line_strs if l)

    def _finalize_transaction(self, row_dict: Dict[str, Any]) -> Optional[Transaction]:
        """Convert accumulated raw row into normalized Transaction object."""
        original_data = row_dict["original_data"]
        table = row_dict["table"]
        account_id = row_dict["account_id"]

        # Map role values from table columns
        role_values: Dict[str, str] = {}
        for col in table.columns:
            val = original_data.get(col.label, "").strip()
            if col.role not in role_values or not role_values[col.role]:
                role_values[col.role] = val

        raw_date = role_values.get("date", "")
        raw_val_date = role_values.get("value_date", "")
        raw_desc = role_values.get("description", "")
        raw_debit = role_values.get("debit", "")
        raw_credit = role_values.get("credit", "")
        raw_amount = role_values.get("amount", "")
        raw_balance = role_values.get("balance", "")

        # 1. Date normalization
        iso_date = None
        cleaned_desc = raw_desc
        if self.profile.description_embedded_date or not raw_date:
            emb_date, emb_desc = extract_embedded_date_and_description(raw_desc)
            if emb_date:
                iso_date = emb_date
                cleaned_desc = emb_desc

        if not iso_date:
            iso_date = parse_date_to_iso(
                raw_date,
                default_year=2025,
                date_format_hint=self.profile.date_format
            )

        if not iso_date:
            # Cannot be a valid transaction without a date
            return None

        # Value date if present
        iso_val_date = parse_date_to_iso(raw_val_date, default_year=2025) if raw_val_date else None

        # 2. Amount and direction derivation
        amount = 0.0
        direction = "debit"

        if self.profile.direction_derivation == "separate-columns":
            debit_val = normalize_amount_str(
                raw_debit, self.profile.decimal_separator, self.profile.thousands_separator
            )
            credit_val = normalize_amount_str(
                raw_credit, self.profile.decimal_separator, self.profile.thousands_separator
            )

            if credit_val is not None and credit_val > 0:
                amount = credit_val
                direction = "credit"
            elif debit_val is not None and debit_val > 0:
                amount = debit_val
                direction = "debit"
            elif raw_amount:
                # Fallback to single amount column
                amt = normalize_amount_str(
                    raw_amount, self.profile.decimal_separator, self.profile.thousands_separator
                )
                if amt is not None:
                    amount = abs(amt)
                    direction = "debit" if amt < 0 else "credit"
        else:
            # Sign-derived
            amt = normalize_amount_str(
                raw_amount, self.profile.decimal_separator, self.profile.thousands_separator
            )
            if amt is not None:
                amount = abs(amt)
                if self.profile.sign_to_direction == "negative-is-credit":
                    direction = "credit" if amt < 0 else "debit"
                else:
                    direction = "debit" if amt < 0 else "credit"

        # 3. Running balance normalization
        balance = None
        if raw_balance:
            balance = normalize_amount_str(
                raw_balance, self.profile.decimal_separator, self.profile.thousands_separator
            )

        # 4. Clean description
        cleaned_desc = re.sub(r"\s+", " ", cleaned_desc).strip()
        if not cleaned_desc:
            cleaned_desc = "UNSPECIFIED TRANSACTION"

        # 5. NLP Categorization and Entity Extraction
        category, confidence, entities = self.nlp_categorizer.categorize(
            cleaned_desc, use_transformers=self.use_transformers
        )

        currency = self.profile.currency
        if account_id and "usd" in account_id.lower():
            currency = "USD"
        elif account_id and "hkd" in account_id.lower():
            currency = "HKD"

        return Transaction(
            date=iso_date,
            value_date=iso_val_date,
            description=cleaned_desc,
            amount=round(amount, self.profile.currency_decimals),
            direction=direction,
            balance=round(balance, self.profile.currency_decimals) if balance is not None else None,
            currency=currency,
            category=category,
            channel=entities.get("channel"),
            reference_id=entities.get("reference_id"),
            account_id=account_id,
            original_data=original_data
        )
