"""
Table detector and column boundary analyzer.
Identifies header rows, column roles, and x-coordinate column intervals on statement pages.
"""

import re
from typing import List, Dict, Tuple, Optional, Any
from app.extraction.coordinate_extractor import ExtractedLine, ExtractedWord
from app.extraction.profiles import BankProfile


# Multi-word phrases that define column roles
MULTI_WORD_PATTERNS = [
    (r"^post\s+date$", "date", "Post Date"),
    (r"^trans\s+date$", "value_date", "Trans Date"),
    (r"^value\s+date$", "value_date", "Value Date"),
    (r"^interest\s+date$", "value_date", "Interest Date"),
    (r"^withdrawal\s*\([-\–]\)$", "debit", "Withdrawal (-)"),
    (r"^deposit\s*\([+\+]\)$", "credit", "Deposit (+)"),
    (r"^chèques\s+et\s+débits(?:\s*\(\$\))?$", "debit", "Chèques et débits ($)"),
    (r"^dépôts\s+et\s+crédits(?:\s*\(\$\))?$", "credit", "Dépôts et crédits ($)"),
    (r"^merchant\s+name(?:\s+or\s+transaction\s+description)?$", "description", "Merchant Name or Transaction Description"),
    (r"^transaction\s+details(?:[\s\n]*進支詳情)?$", "description", "Transaction Details"),
    (r"^\$\s*amount$", "amount", "$ Amount"),
    (r"^solde(?:\s*\(\$\))?$", "balance", "Solde ($)"),
    (r"^chq\s+no$", "reference", "Chq No"),
]

SINGLE_WORD_PATTERNS = [
    (r"^(?:date|datum|تاريخ|日期)$", "date", "Date"),
    (r"^(?:description|details|détails|particulars|narration|進支詳情|البيان)$", "description", "Description"),
    (r"^(?:withdrawal|debit|提取|مدين)$", "debit", "Withdrawal"),
    (r"^(?:deposit|credit|存入|دائن)$", "credit", "Deposit"),
    (r"^(?:amount|bedrag|montant|المبلغ)$", "amount", "Amount"),
    (r"^(?:balance|solde|saldo|結餘|الرصيد)$", "balance", "Balance"),
    (r"^(?:counterparty|tegenrekening)$", "counterparty", "Counterparty"),
    (r"^(?:ref|reference|المرجع)$", "reference", "Reference"),
]


class ColumnInterval:
    def __init__(self, role: str, label: str, x0: float, x1: float):
        self.role = role
        self.label = label
        self.x0 = x0
        self.x1 = x1

    def contains_x(self, x: float) -> bool:
        return self.x0 <= x <= self.x1

    def __repr__(self):
        return f"Col({self.role}: {self.label} [{self.x0:.1f}, {self.x1:.1f}])"


class DetectedTable:
    def __init__(
        self,
        page_num: int,
        header_y0: float,
        header_line: ExtractedLine,
        columns: List[ColumnInterval],
        account_id: Optional[str] = None
    ):
        self.page_num = page_num
        self.header_y0 = header_y0
        self.header_line = header_line
        self.columns = columns
        self.account_id = account_id

    def map_word_to_column(self, word: ExtractedWord) -> Optional[str]:
        """Find matching column role for a given word by x-coordinate."""
        w_center = (word.x0 + word.x1) / 2.0
        for col in self.columns:
            if col.contains_x(w_center):
                return col.role
        # Fallback to closest column
        closest_col = None
        min_dist = float("inf")
        for col in self.columns:
            dist = min(abs(w_center - col.x0), abs(w_center - col.x1))
            if dist < min_dist:
                min_dist = dist
                closest_col = col.role
        return closest_col


class TableDetector:
    """Detects tabular structure and column intervals in bank statements."""

    def __init__(self, profile: Optional[BankProfile] = None):
        self.profile = profile

    def detect_table_on_page(
        self,
        lines: List[ExtractedLine],
        page_width: float,
        page_num: int,
        account_id: Optional[str] = None
    ) -> Optional[DetectedTable]:
        """Search lines for table header row and compute column boundaries."""
        for line in lines:
            columns = self._build_column_intervals(line, page_width)
            if len(columns) >= 3:
                return DetectedTable(
                    page_num=page_num,
                    header_y0=line.y0,
                    header_line=line,
                    columns=columns,
                    account_id=account_id
                )
        return None

    def _build_column_intervals(
        self,
        header_line: ExtractedLine,
        page_width: float
    ) -> List[ColumnInterval]:
        """Parse words in header line into distinct column anchors."""
        words = header_line.words
        anchors = []
        i = 0
        while i < len(words):
            matched = False
            # Try 5-word, 4-word, 3-word, 2-word spans first
            for span_len in [5, 4, 3, 2]:
                if i + span_len <= len(words):
                    candidate_span = words[i : i + span_len]
                    cand_text = " ".join(w.text for w in candidate_span).strip()
                    for pat, role, label in MULTI_WORD_PATTERNS:
                        if re.match(pat, cand_text, re.IGNORECASE):
                            anchors.append({
                                "role": role,
                                "label": label,
                                "x0": candidate_span[0].x0,
                                "x1": candidate_span[-1].x1,
                                "x_center": (candidate_span[0].x0 + candidate_span[-1].x1) / 2.0
                            })
                            i += span_len
                            matched = True
                            break
                    if matched:
                        break
            if matched:
                continue

            # Try single word
            w = words[i]
            w_text = w.text.strip()
            for pat, role, label in SINGLE_WORD_PATTERNS:
                if re.match(pat, w_text, re.IGNORECASE):
                    anchors.append({
                        "role": role,
                        "label": label,
                        "x0": w.x0,
                        "x1": w.x1,
                        "x_center": (w.x0 + w.x1) / 2.0
                    })
                    matched = True
                    break
            i += 1

        if len(anchors) < 3:
            return []

        # Sort anchors left-to-right
        anchors.sort(key=lambda a: a["x_center"])

        # Partition x boundaries between adjacent column anchors
        intervals: List[ColumnInterval] = []
        for idx in range(len(anchors)):
            cur = anchors[idx]
            role = cur["role"]
            label = cur["label"]

            if idx == 0:
                x_start = 0.0
            else:
                prev = anchors[idx - 1]
                x_start = (prev["x1"] + cur["x0"]) / 2.0

            if idx == len(anchors) - 1:
                x_end = page_width
            else:
                nxt = anchors[idx + 1]
                x_end = (cur["x1"] + nxt["x0"]) / 2.0

            intervals.append(ColumnInterval(role=role, label=label, x0=x_start, x1=x_end))

        return intervals
