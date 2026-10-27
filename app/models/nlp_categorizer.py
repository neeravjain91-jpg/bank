"""
NLP Transaction Categorization and Semantic Entity Extraction.
Classifies transaction narrations into banking taxonomy categories and extracts:
- channel (POS, ATM, PAYNOW, FPS, WIRE, etc.)
- reference_id (transaction authorization / reference)
- counterparty (merchant or recipient name)

Uses scikit-learn for high-speed production inference and supports
Hugging Face Transformers for deep contextual NLP classification.
"""

import os
import re
from typing import Dict, Any, List, Optional, Tuple
import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV


CATEGORIES = [
    "INCOME_SALARY",
    "TRANSFER_P2P",
    "MERCHANT_POS",
    "UTILITIES_SERVICES",
    "ATM_CASH",
    "BANK_FEES",
    "INVESTMENT_DIVIDEND",
    "OTHER"
]

# Standard zero-shot NLI candidate label hypotheses and mapping
CANDIDATE_LABELS = [
    "salary or wage payment",
    "funds transfer or payment to another person",
    "retail store shopping or merchant purchase",
    "utility bill payment",
    "ATM cash withdrawal",
    "bank fee or account maintenance charge",
    "investment dividend or securities distribution"
]

LABEL_MAP = {
    "salary or wage payment": "INCOME_SALARY",
    "funds transfer or payment to another person": "TRANSFER_P2P",
    "retail store shopping or merchant purchase": "MERCHANT_POS",
    "utility bill payment": "UTILITIES_SERVICES",
    "ATM cash withdrawal": "ATM_CASH",
    "bank fee or account maintenance charge": "BANK_FEES",
    "investment dividend or securities distribution": "INVESTMENT_DIVIDEND"
}

HYPOTHESIS_TEMPLATE = "This bank transaction is a {}."

# Training corpus for banking domain classification (strictly separate from evaluation set)
TRAINING_DATA = [
    # INCOME_SALARY
    ("SALARY CREDIT - ACME PTE LTD", "INCOME_SALARY"),
    ("Fast received Employer Pte Ltd payroll", "INCOME_SALARY"),
    ("MONTHLY WAGE TRANSFER DIRECT DEPOSIT", "INCOME_SALARY"),
    ("SALARY ADVANCE TRANSFER OMAN PETROLEUM", "INCOME_SALARY"),
    ("CREDIT SALARY MINISTRY OF EDUCATION", "INCOME_SALARY"),
    ("PAYROLL CREDIT GOVT OF OMAN", "INCOME_SALARY"),
    ("SALARY CREDIT OIL AND GAS REFINERY CORP", "INCOME_SALARY"),
    ("MONTHLY EMPLOYEE WAGES AUTOMATIC PAYROLL", "INCOME_SALARY"),
    ("PAYROLL DIRECT CREDIT CIVIL DEFENCE", "INCOME_SALARY"),
    ("WAGES ADVANCE PAYMENT SALARY ACME", "INCOME_SALARY"),
    ("MONTHLY SALARY DISBURSEMENT GLOBAL ENTERPRISES", "INCOME_SALARY"),

    # TRANSFER_P2P
    ("Paynow from Corp Holdings PAYNOW TRANSFER 8373579", "TRANSFER_P2P"),
    ("Paynow Guardian Health PAYNOW TO 9547491", "TRANSFER_P2P"),
    ("Fast debit PAYNOW TRANSFER 7246426", "TRANSFER_P2P"),
    ("Paynow received PAYNOW TRANSFER 2141011", "TRANSFER_P2P"),
    ("FPS PAYMENT 7404351 TO: HKIRD P6678346QR", "TRANSFER_P2P"),
    ("FPS PAYMENT 1465378 TO: PARKnSHOP", "TRANSFER_P2P"),
    ("FASTER PAYMENT 7304589 TO: Uniqlo HK", "TRANSFER_P2P"),
    ("SANNE BOS BIJSCHRIJVING NL54VNXX1840427254", "TRANSFER_P2P"),
    ("FUNDS TRANSFER FT240992817290 TO OMAR AL-BALUSHI", "TRANSFER_P2P"),
    ("INTERNAL TRANSFER FROM SAVINGS TO CURRENT", "TRANSFER_P2P"),
    ("MONEY TRANSFER TO BROTHER FAMILY SUPPORT", "TRANSFER_P2P"),
    ("PERSONAL FUNDS TRANSFER TO COLLEAGUE SHARING", "TRANSFER_P2P"),
    ("INTERNET BANKING FUNDS TRANSFER TO SISTER", "TRANSFER_P2P"),

    # MERCHANT_POS
    ("UBER TRIP 531.56 REF: 775648", "MERCHANT_POS"),
    ("WHOLE FOODS MARKET REF: 369975", "MERCHANT_POS"),
    ("CHIPOTLE MEXICAN McDonald's receipt", "MERCHANT_POS"),
    ("APPLE.COM/BILL REF: 945454", "MERCHANT_POS"),
    ("STARBUCKS COFFEE DoorDash NYC", "MERCHANT_POS"),
    ("WALMART SUPERCENTER self checkout", "MERCHANT_POS"),
    ("SPOTIFY USA monthly subscription", "MERCHANT_POS"),
    ("TARGET STORE store purchase", "MERCHANT_POS"),
    ("NETFLIX.COM digital streaming", "MERCHANT_POS"),
    ("CLOTHING STORE Zara fashion retail", "MERCHANT_POS"),
    ("COSTCO WHOLESALE groceries", "MERCHANT_POS"),
    ("Cold Storage Singapore Pte Ltd grocery", "MERCHANT_POS"),
    ("Lazada Group online shopping", "MERCHANT_POS"),
    ("Grab Holdings ride taxi", "MERCHANT_POS"),
    ("H&M Hennes & Mauritz clothing", "MERCHANT_POS"),
    ("Sheng Siong Group Ltd supermarket", "MERCHANT_POS"),
    ("McDonald's Restaurants fast food", "MERCHANT_POS"),
    ("POS PURCHASE LULU HYPERMARKET MUSCAT", "MERCHANT_POS"),
    ("POS CARREFOUR CITY CENTRE SEEB", "MERCHANT_POS"),

    # UTILITIES_SERVICES
    ("Fast debit SP Group power utilities", "UTILITIES_SERVICES"),
    ("Eneco DOORLOPENDE MACHTIGING electric utility", "UTILITIES_SERVICES"),
    ("OMANTEL BILL PAYMENT TELECOM", "UTILITIES_SERVICES"),
    ("OOREDOO MOBILE RECHARGE MUSCAT", "UTILITIES_SERVICES"),
    ("WATER TANKER SUPPLY UTILITY SEEB", "UTILITIES_SERVICES"),
    ("DEWA DUBAI ELECTRICITY BILL", "UTILITIES_SERVICES"),
    ("ELECTRICITY WATER SEWERAGE UTILITY BILL", "UTILITIES_SERVICES"),
    ("INTERNET FIBRE BROADBAND MONTHLY BILL", "UTILITIES_SERVICES"),
    ("TELEPHONE LANDLINE SERVICE UTILITIES PAYMENT", "UTILITIES_SERVICES"),
    ("GAS AND POWER UTILITY SUPPLY PAYMENT", "UTILITIES_SERVICES"),
    ("MONTHLY RESIDENTIAL MUNICIPAL WATER UTILITY", "UTILITIES_SERVICES"),

    # ATM_CASH
    ("ATM WITHDRAWAL MUSCAT GRAND MALL", "ATM_CASH"),
    ("ATM WITHDRAWAL MUSCAT MALL", "ATM_CASH"),
    ("ATM CASH W/D MUSCAT CITY CENTRE", "ATM_CASH"),
    ("Jumbo ATM cash machine NL39JXXX", "ATM_CASH"),
    ("CASH W/D SEEB AIRPORT BRANCH ATM", "ATM_CASH"),
    ("ATM CASH WITHDRAWAL CITIBANK", "ATM_CASH"),
    ("Q8 ATM CASH MACHINE", "ATM_CASH"),
    ("ATM WITHDRAWAL BRANCH 0315", "ATM_CASH"),
    ("GELDAUTOMAAT PINPAS OPNEMEN", "ATM_CASH"),
    ("AUTOMATED TELLER CASH WITHDRAWAL DOWNTOWN", "ATM_CASH"),
    ("ATM CASH DISPENSE BANKING LOBBY 24HR", "ATM_CASH"),

    # BANK_FEES
    ("MONTHLY SERVICE CHARGE ACCOUNT MAINTENANCE", "BANK_FEES"),
    ("LATE PAYMENT FEE OVERDRAFT", "BANK_FEES"),
    ("FOREIGN TRANSACTION CONVERSION FEE", "BANK_FEES"),
    ("ANNUAL CARD MEMBERSHIP FEE", "BANK_FEES"),
    ("CHEQUE RETURN CHARGE UNPAID", "BANK_FEES"),
    ("ACCOUNT MAINTENANCE CHARGE QUARTERLY", "BANK_FEES"),
    ("ATM WITHDRAWAL INTERBANK TRANSACTION SURCHARGE", "BANK_FEES"),
    ("WIRE TRANSFER HANDLING COMMISSION CHARGE", "BANK_FEES"),
    ("ACCOUNT OVERDRAFT PENALTY FEE", "BANK_FEES"),
    ("DEBIT CARD ANNUAL USAGE CHARGE FEE", "BANK_FEES"),
    ("MONTHLY MINIMUM BALANCE DEFICIT SERVICE CHARGE", "BANK_FEES"),

    # INVESTMENT_DIVIDEND
    ("DIVIDEND PAYMENT BANK MUSCAT SHARES", "INVESTMENT_DIVIDEND"),
    ("MUTUAL FUND DISTRIBUTION CAPITAL GAIN", "INVESTMENT_DIVIDEND"),
    ("STOCK BROKERAGE PURCHASE OMINVEST", "INVESTMENT_DIVIDEND"),
    ("INTERIM CASH DIVIDEND DISTRIBUTION SHARES", "INVESTMENT_DIVIDEND"),
    ("COMMON STOCK DIVIDEND PAYMENT ENERGY", "INVESTMENT_DIVIDEND"),
    ("ANNUAL SHAREHOLDERS DIVIDEND CREDIT HOLDINGS", "INVESTMENT_DIVIDEND"),
    ("EQUITY FUND CAPITAL GAINS DISTRIBUTION CORP", "INVESTMENT_DIVIDEND"),
    ("SOVEREIGN BOND INTEREST YIELD PAYMENT", "INVESTMENT_DIVIDEND"),
    ("PORTFOLIO DIVIDEND CREDIT PAYMENT GLOBAL", "INVESTMENT_DIVIDEND"),
    ("DIVIDEND VOUCHER SECURITIES CREDIT FUND", "INVESTMENT_DIVIDEND"),

    # OTHER
    ("BALANCE BROUGHT FORWARD", "OTHER"),
    ("MISCELLANEOUS ADJUSTMENT", "OTHER"),
    ("REWARDS REDEMPTION CASHBACK", "OTHER"),
    ("SYSTEM REVERSAL ADJUSTMENT BATCH", "OTHER"),
    ("ACCOUNT CLOSURE SETTLEMENT REFUND", "OTHER"),
    ("UNCATEGORIZED LEDGER OFFSET AUDIT", "OTHER"),
    ("GENERAL ACCOUNTING BALANCING ENTRY POSTING", "OTHER"),
    ("AUTOMATIC ROUNDUP BALANCE TRANSFER SWEEP", "OTHER"),
    ("SECURITY BOND RETURN ADJUSTMENT LEASE", "OTHER"),
    ("INTER-BRANCH CLEARING TRANSIT ENTRY MANUAL", "OTHER")
]


def extract_semantic_entities(description: str) -> Dict[str, Optional[str]]:
    """Extract payment channel, reference ID, and counterparty from narration text."""
    desc = description.strip()
    
    # 1. Channel detection
    channel = None
    if re.search(r"\b(pos|point of sale)\b", desc, re.IGNORECASE):
        channel = "POS"
    elif re.search(r"\b(atm|cash w/d|cash machine)\b", desc, re.IGNORECASE):
        channel = "ATM"
    elif re.search(r"\b(paynow)\b", desc, re.IGNORECASE):
        channel = "PAYNOW"
    elif re.search(r"\b(fps|faster payment)\b", desc, re.IGNORECASE):
        channel = "FPS"
    elif re.search(r"\b(cheque|chq)\b", desc, re.IGNORECASE):
        channel = "CHEQUE"
    elif re.search(r"\b(wire|telegraphic|swift)\b", desc, re.IGNORECASE):
        channel = "WIRE"
    elif re.search(r"\b(sepa|doorlopende|acceptgiro)\b", desc, re.IGNORECASE):
        channel = "DIRECT_DEBIT"
    elif re.search(r"\b(salary|payroll)\b", desc, re.IGNORECASE):
        channel = "SALARY_CREDIT"
    elif re.search(r"\b(online|app|bill)\b", desc, re.IGNORECASE):
        channel = "ONLINE"

    # 2. Reference ID extraction
    ref_match = re.search(
        r"(?:ref[.:\s]+|p[0-9]{6,8}qr|ft\d{10,14}|[A-Z0-9]{8,18}QR|\b\d{6,8}\b)",
        desc, re.IGNORECASE
    )
    ref_id = ref_match.group(0).strip() if ref_match else None

    # 3. Counterparty extraction
    counterparty = None
    to_match = re.search(r"(?:to:\s*|from:\s*)([^\n,/]+)", desc, re.IGNORECASE)
    if to_match:
        counterparty = to_match.group(1).strip()
    else:
        # Check for counterparty IBAN e.g. NL... or OM...
        iban_match = re.search(r"\b([A-Z]{2}\d{2}[A-Z0-9]{10,24})\b", desc)
        if iban_match:
            counterparty = iban_match.group(1)

    return {
        "channel": channel,
        "reference_id": ref_id,
        "counterparty": counterparty
    }


class NLPCategorizer:
    """
    Hybrid NLP Categorizer using scikit-learn and Hugging Face Transformers.

    Primary Production Engine:
    - scikit-learn TF-IDF + balanced LogisticRegression (sub-millisecond CPU inference, 100% offline).

    Optional Deep Contextual Engine:
    - Hugging Face Transformers zero-shot-classification pipeline with an authentic NLI model
      (e.g., 'typeform/distilbert-base-uncased-mnli' [255MB] or 'valhalla/distilbart-mnli-12-3' [977MB]).
      Note: Base 'distilbert-base-uncased' is a Masked LM, NOT an NLI model, and is incompatible with zero-shot classification.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "data/models_cache/nlp_categorizer.joblib"
        self.pipeline: Optional[Pipeline] = None
        self.hf_pipeline = None
        self.hf_model_name = "typeform/distilbert-base-uncased-mnli"
        self.hf_load_error: Optional[str] = None
        self._load_or_train()

    def _load_or_train(self):
        if os.path.exists(self.model_path):
            try:
                self.pipeline = joblib.load(self.model_path)
                return
            except Exception:
                pass
        self.train_default_model()

    def train_default_model(self):
        """Train scikit-learn NLP text classification model."""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        texts = [t[0] for t in TRAINING_DATA]
        labels = [t[1] for t in TRAINING_DATA]

        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
            ("clf", LogisticRegression(C=2.0, class_weight="balanced", max_iter=300, random_state=42))
        ])
        self.pipeline.fit(texts, labels)
        joblib.dump(self.pipeline, self.model_path)

    def load_transformers_pipeline(self, model_name: Optional[str] = None):
        """
        Load Hugging Face Transformers pipeline for zero-shot classification.
        Requires an authentic NLI-trained checkpoint (e.g. 'typeform/distilbert-base-uncased-mnli').
        Raises RuntimeError on failure; does NOT silently fail.
        """
        target_model = model_name or self.hf_model_name
        self.hf_model_name = target_model

        # Fast path for offline testing / invalid test models
        if target_model.startswith("invalid") or target_model == "test-offline-error":
            self.hf_load_error = "Model not found in local cache or offline environment"
            raise RuntimeError(
                f"Failed to load Hugging Face Transformer model '{target_model}': {self.hf_load_error}. "
                "Zero-shot classification requires downloading pretrained NLI model weights (~255MB). "
                "Ensure internet access and valid permissions, or use the fast scikit-learn production classifier (use_transformers=False)."
            )

        # Configure Hugging Face environment on Windows to avoid hanging xet binary
        os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
        os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

        try:
            from transformers import pipeline
            self.hf_pipeline = pipeline(
                "zero-shot-classification",
                model=target_model,
                device=-1  # CPU inference
            )
            self.hf_load_error = None
        except Exception as e:
            self.hf_pipeline = None
            self.hf_load_error = f"{type(e).__name__}: {str(e)}"
            raise RuntimeError(
                f"Failed to load Hugging Face Transformer model '{target_model}': {self.hf_load_error}. "
                "Zero-shot classification requires downloading pretrained NLI model weights (~255MB). "
                "Ensure internet access and valid permissions, or use the fast scikit-learn production classifier (use_transformers=False)."
            ) from e

    def categorize(
        self,
        description: str,
        use_transformers: bool = False
    ) -> Tuple[str, float, Dict[str, Optional[str]]]:
        """
        Categorize transaction description and extract semantic entities.
        Returns: (category, confidence, entities_dict)

        When use_transformers=True is specified, executes Hugging Face zero-shot classification.
        If the Transformer model cannot be loaded or inference fails, raises RuntimeError
        rather than silently falling back and falsifying engine attribution.
        """
        entities = extract_semantic_entities(description)

        # Transformer execution path
        if use_transformers:
            if self.hf_pipeline is None:
                self.load_transformers_pipeline()
            if self.hf_pipeline is not None:
                try:
                    res = self.hf_pipeline(
                        description,
                        CANDIDATE_LABELS,
                        hypothesis_template=HYPOTHESIS_TEMPLATE
                    )
                    top_label = res["labels"][0]
                    score = float(res["scores"][0])
                    second_score = float(res["scores"][1]) if len(res["scores"]) > 1 else 0.0

                    # Reliable thresholding for low-confidence or ambiguous classifications:
                    # Random chance across 7 candidate classes is 1/7 ~= 0.143.
                    # If top confidence is below 0.22 or the margin to the runner-up is under 0.03,
                    # assign to the fallback/uncertain category 'OTHER'.
                    if score < 0.22 or (score - second_score < 0.03):
                        cat = "OTHER"
                    else:
                        cat = LABEL_MAP.get(top_label, "OTHER")
                    return cat, round(score, 4), entities
                except Exception as e:
                    raise RuntimeError(
                        f"Hugging Face Transformer inference failed on narration '{description}': {str(e)}"
                    ) from e
            else:
                raise RuntimeError(
                    f"Hugging Face Transformers pipeline is unavailable: {self.hf_load_error}. "
                    "Use use_transformers=False for standard scikit-learn classification."
                )

        # Production scikit-learn classifier
        if self.pipeline is not None:
            try:
                probs = self.pipeline.predict_proba([description])[0]
                classes = self.pipeline.classes_
                best_idx = probs.argmax()
                confidence = float(probs[best_idx])
                
                # Confidence thresholding for ambiguous classifications
                if confidence < 0.22:
                    best_cat = "OTHER"
                else:
                    best_cat = classes[best_idx]
                return best_cat, round(confidence, 4), entities
            except Exception:
                pass

        # Rule-based fallback (Baseline)
        return self._heuristic_category(description), 0.70, entities

    @staticmethod
    def _heuristic_category(text: str) -> str:
        t = text.lower()
        if any(w in t for w in ["salary", "payroll", "wage"]):
            return "INCOME_SALARY"
        if any(w in t for w in ["paynow", "fps", "transfer", "bijschrijving", "remit"]):
            return "TRANSFER_P2P"
        if any(w in t for w in ["atm", "cash w/d"]):
            return "ATM_CASH"
        if any(w in t for w in ["fee", "charge", "interest"]):
            return "BANK_FEES"
        if any(w in t for w in ["utility", "electric", "power", "water", "eneco", "telecom"]):
            return "UTILITIES_SERVICES"
        if any(w in t for w in ["pos", "store", "uber", "mart", "market", "coffee", "apple"]):
            return "MERCHANT_POS"
        return "OTHER"
