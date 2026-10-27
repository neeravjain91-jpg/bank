"""
Pydantic schemas for bank statement table extraction, validation, and analytics.
"""

from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field


class Transaction(BaseModel):
    """Normalized transaction row with full traceability to raw document data."""
    date: str = Field(..., description="Transaction date in ISO-8601 format (YYYY-MM-DD)")
    value_date: Optional[str] = Field(None, description="Value or settlement date (YYYY-MM-DD)")
    description: str = Field(..., description="Cleaned, normalized transaction narration/description")
    amount: float = Field(..., description="Absolute transaction amount (positive float)")
    direction: Literal["debit", "credit"] = Field(..., description="Direction: debit (withdrawal) or credit (deposit)")
    balance: Optional[float] = Field(None, description="Running account balance after transaction")
    currency: Optional[str] = Field(None, description="ISO currency code (e.g., OMR, SGD, USD, EUR, CAD, HKD)")
    
    # NLP & Banking Analytics Enrichments
    category: Optional[str] = Field(None, description="ML/NLP predicted transaction category (e.g. INCOME_SALARY, MERCHANT_POS, UTILITIES)")
    channel: Optional[str] = Field(None, description="Payment rails or transaction channel (e.g. POS, ATM, PAYNOW, FPS, WIRE, CHEQUE)")
    reference_id: Optional[str] = Field(None, description="Extracted transaction reference number or authorization code")
    account_id: Optional[str] = Field(None, description="Account identifier for multi-account statements")
    
    # Audit Traceability (Bankstatemently benchmark compliant)
    original_data: Dict[str, str] = Field(
        default_factory=dict,
        description="Verbatim raw cell/column values extracted directly from the document"
    )

    def to_benchmark_dict(self) -> Dict[str, Any]:
        """Convert to canonical Bankstatemently benchmark evaluation format."""
        d: Dict[str, Any] = {
            "date": self.date,
            "description": self.description,
            "amount": round(self.amount, 3),
            "direction": self.direction,
            "originalData": self.original_data,
        }
        if self.balance is not None:
            d["balance"] = round(self.balance, 3)
        if self.currency is not None:
            d["currency"] = self.currency
        if self.account_id is not None:
            d["accountId"] = self.account_id
        return d


class Account(BaseModel):
    """Account metadata extracted from statement header."""
    id: str = Field(..., description="Internal account handle/identifier")
    account_number: Optional[str] = Field(None, description="Verbatim account number")
    name: Optional[str] = Field(None, description="Account holder name or account title")
    iban: Optional[str] = Field(None, description="International Bank Account Number if present")
    currency: Optional[str] = Field(None, description="Account currency")
    opening_balance: Optional[float] = Field(None, description="Statement opening balance")
    closing_balance: Optional[float] = Field(None, description="Statement closing balance")

    def to_benchmark_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"id": self.id}
        if self.account_number:
            d["accountNumber"] = self.account_number
        if self.name:
            d["name"] = self.name
        if self.currency:
            d["currency"] = self.currency
        return d


class BalanceValidationResult(BaseModel):
    """Accounting balance check results."""
    reconciled: bool = Field(..., description="Whether all running balance and closing balance checks passed")
    opening_balance: Optional[float] = Field(None, description="Opening balance from document")
    closing_balance: Optional[float] = Field(None, description="Closing balance reported in document")
    calculated_closing_balance: Optional[float] = Field(None, description="Opening balance + Total credits - Total debits")
    total_debits: float = Field(0.0, description="Sum of all debit transactions")
    total_credits: float = Field(0.0, description="Sum of all credit transactions")
    net_change: float = Field(0.0, description="Total credits minus total debits")
    discrepancy_count: int = Field(0, description="Number of running balance discrepancies detected")
    discrepancies: List[Dict[str, Any]] = Field(default_factory=list, description="Detailed discrepancy events")
    warnings: List[str] = Field(default_factory=list, description="Accounting validation warnings")


class ExtractionMetadata(BaseModel):
    """Metadata regarding the PDF extraction run."""
    content_hash: str = Field(..., description="SHA-256 hash of the input document")
    file_name: str = Field(..., description="Name of the processed file")
    page_count: int = Field(..., description="Total pages in document")
    bank: Optional[str] = Field(None, description="Detected or specified bank")
    profile_used: str = Field(..., description="Parser profile used for extraction")
    currency: Optional[str] = Field(None, description="Primary detected currency")
    transaction_count: int = Field(..., description="Total extracted transactions")
    extraction_method: str = Field("ml_enhanced", description="'ml_enhanced' or 'baseline_rules'")
    processing_time_seconds: float = Field(..., description="Execution duration in seconds")


class ExtractionResponse(BaseModel):
    """Standard response model for POST /extract."""
    metadata: ExtractionMetadata
    accounts: List[Account] = Field(default_factory=list)
    transactions: List[Transaction] = Field(default_factory=list)
    validation: BalanceValidationResult

    def to_benchmark_submission(self) -> Dict[str, Any]:
        """Convert entire response to Bankstatemently submission JSON."""
        sub: Dict[str, Any] = {
            "contentHash": self.metadata.content_hash,
            "transactions": [t.to_benchmark_dict() for t in self.transactions]
        }
        if self.accounts:
            sub["accounts"] = [a.to_benchmark_dict() for a in self.accounts]
        return sub


class CategorizeRequest(BaseModel):
    """Request for NLP categorization endpoint."""
    descriptions: List[str] = Field(..., description="List of transaction descriptions to categorize")
    use_transformers: bool = Field(False, description="Whether to use Hugging Face transformers or fast ML classifier")


class CategorizeResult(BaseModel):
    """Result of NLP categorization."""
    description: str
    category: str
    confidence: float
    channel: Optional[str] = None
    reference_id: Optional[str] = None
    counterparty: Optional[str] = None


class CategorizeResponse(BaseModel):
    results: List[CategorizeResult]
    model_used: str
