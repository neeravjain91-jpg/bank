"""
High-Level Statement Extraction Orchestrator Service.
Coordinates document inspection, coordinate extraction, ML line classification,
transaction assembly, normalization, and accounting balance reconciliation.
"""

import time
import io
import csv
from typing import Optional, Union, Dict, Any, List
import pymupdf

from app.extraction.coordinate_extractor import CoordinateExtractor, compute_pdf_hash
from app.extraction.profiles import BankProfile, get_profile, detect_profile_from_text
from app.extraction.assembler import TransactionAssembler
from app.models.line_classifier import LineClassifier
from app.models.nlp_categorizer import NLPCategorizer
from app.validation.balance_checker import validate_statement_balances
from app.schemas.transaction import (
    Transaction,
    Account,
    BalanceValidationResult,
    ExtractionMetadata,
    ExtractionResponse
)


class StatementExtractorService:
    """End-to-end bank statement table extraction service."""

    def __init__(
        self,
        line_classifier: Optional[LineClassifier] = None,
        nlp_categorizer: Optional[NLPCategorizer] = None
    ):
        self.line_classifier = line_classifier or LineClassifier()
        self.nlp_categorizer = nlp_categorizer or NLPCategorizer()
        self.coord_extractor = CoordinateExtractor()

    def extract_from_bytes(
        self,
        pdf_bytes: bytes,
        file_name: str = "statement.pdf",
        profile_id: Optional[str] = "auto",
        use_ml: bool = True,
        use_transformers: bool = False
    ) -> ExtractionResponse:
        """Extract transactions from in-memory PDF bytes."""
        t_start = time.time()
        content_hash = compute_pdf_hash(pdf_bytes)

        # Open PDF
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        page_count = len(doc)

        # Inspect text layer
        full_text = ""
        total_words = 0
        for page in doc:
            t = page.get_text()
            full_text += t + "\n"
            total_words += len(t.split())

        if total_words == 0 and page_count > 0:
            # Scanned document detection
            proc_time = round(time.time() - t_start, 4)
            return ExtractionResponse(
                metadata=ExtractionMetadata(
                    content_hash=content_hash,
                    file_name=file_name,
                    page_count=page_count,
                    bank="scanned-document",
                    profile_used="none",
                    currency=None,
                    transaction_count=0,
                    extraction_method="scanned_detected",
                    processing_time_seconds=proc_time
                ),
                accounts=[],
                transactions=[],
                validation=BalanceValidationResult(
                    reconciled=False,
                    warnings=["Document has no selectable digital text layer (scanned PDF image)."]
                )
            )

        # Determine Profile
        if profile_id and profile_id.lower() != "auto":
            profile = get_profile(profile_id)
        else:
            profile = detect_profile_from_text(full_text)

        # Extract coordinates and lines
        page_lines = self.coord_extractor.extract_document_lines(doc)

        # Assemble transactions using ML
        assembler = TransactionAssembler(
            profile=profile,
            line_classifier=self.line_classifier,
            nlp_categorizer=self.nlp_categorizer,
            use_ml=use_ml,
            use_transformers=use_transformers
        )
        transactions, accounts, op_bal, cl_bal = assembler.assemble(doc, page_lines)

        # Validate balances
        account_type = "credit_card" if profile.sign_to_direction == "negative-is-credit" else "deposit"
        validation = validate_statement_balances(
            transactions=transactions,
            opening_balance=op_bal,
            reported_closing_balance=cl_bal,
            account_type=account_type
        )

        proc_time = round(time.time() - t_start, 4)
        metadata = ExtractionMetadata(
            content_hash=content_hash,
            file_name=file_name,
            page_count=page_count,
            bank=profile.name,
            profile_used=profile.id,
            currency=profile.currency,
            transaction_count=len(transactions),
            extraction_method="ml_enhanced" if use_ml else "baseline_rules",
            processing_time_seconds=proc_time
        )

        return ExtractionResponse(
            metadata=metadata,
            accounts=accounts,
            transactions=transactions,
            validation=validation
        )

    def extract_from_path(
        self,
        pdf_path: str,
        profile_id: Optional[str] = "auto",
        use_ml: bool = True,
        use_transformers: bool = False
    ) -> ExtractionResponse:
        """Extract transactions from file on disk."""
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        import os
        fname = os.path.basename(pdf_path)
        return self.extract_from_bytes(
            pdf_bytes=pdf_bytes,
            file_name=fname,
            profile_id=profile_id,
            use_ml=use_ml,
            use_transformers=use_transformers
        )

    @staticmethod
    def to_csv(response: ExtractionResponse) -> str:
        """Serialize extracted transactions to CSV string."""
        output = io.StringIO()
        fieldnames = [
            "date", "value_date", "description", "amount", "direction",
            "balance", "currency", "category", "channel", "reference_id", "account_id"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for txn in response.transactions:
            writer.writerow({
                "date": txn.date,
                "value_date": txn.value_date or "",
                "description": txn.description,
                "amount": f"{txn.amount:.3f}",
                "direction": txn.direction,
                "balance": f"{txn.balance:.3f}" if txn.balance is not None else "",
                "currency": txn.currency or "",
                "category": txn.category or "",
                "channel": txn.channel or "",
                "reference_id": txn.reference_id or "",
                "account_id": txn.account_id or ""
            })
        return output.getvalue()
