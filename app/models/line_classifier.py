"""
Machine Learning Line Classifier for Bank Statement Layouts.
Uses scikit-learn to classify extracted text lines into:
- TABLE_HEADER
- TRANSACTION_START
- TRANSACTION_CONTINUATION
- METADATA_HEADER
- BALANCE_SUMMARY
- NOISE_FOOTER
"""

import os
import re
from typing import List, Dict, Any, Optional, Tuple
import joblib
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report


CLASSES = [
    "TABLE_HEADER",
    "TRANSACTION_START",
    "TRANSACTION_CONTINUATION",
    "METADATA_HEADER",
    "BALANCE_SUMMARY",
    "NOISE_FOOTER"
]

HEADER_KEYWORDS = {
    "date", "description", "details", "détails", "narration", "particulars",
    "withdrawal", "deposit", "balance", "solde", "debit", "credit", "post date",
    "trans date", "amount", "bedrag", "tegenrekening", "counterparty", "chq no",
    "進支詳情", "存入", "提取", "結餘"
}

FOOTER_KEYWORDS = {
    "page", "terms and conditions", "deposit insurance", "rekeningafschrift",
    "all rights reserved", "licensed by", "corporate office", "member fdic",
    "guarantee scheme", "please examine", "discrepancy"
}

BALANCE_KEYWORDS = {
    "balance brought forward", "balance carried forward", "solde d'ouverture",
    "solde de fermeture", "opening balance", "closing balance", "total debits",
    "total credits", "totals year-to-date", "total no. of deposits"
}


def extract_features_from_line(
    text: str,
    bbox: Tuple[float, float, float, float],
    page_width: float,
    page_height: float,
    prev_label: Optional[str] = None
) -> Dict[str, Any]:
    """Extract spatial, lexical, and regex features from a line."""
    x0, y0, x1, y1 = bbox
    t_clean = text.strip()
    words = t_clean.split()
    length = len(t_clean)
    num_words = len(words)

    # Spatial features
    rel_y0 = y0 / page_height if page_height > 0 else 0.0
    rel_x0 = x0 / page_width if page_width > 0 else 0.0
    line_w = (x1 - x0) / page_width if page_width > 0 else 0.0
    line_h = y1 - y0

    # Lexical features
    num_digits = sum(c.isdigit() for c in t_clean)
    digit_ratio = num_digits / length if length > 0 else 0.0
    num_upper = sum(c.isupper() for c in t_clean)
    upper_ratio = num_upper / length if length > 0 else 0.0

    # Regex indicators
    # Date at start of line
    starts_with_date = bool(re.match(
        r"^(\d{1,2}[/\-\.]\d{1,2}|\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|mei|janv))",
        t_clean, re.IGNORECASE
    ))
    has_date = bool(re.search(r"\d{1,2}[/\-\.]\d{1,2}|\d{4}[-/]\d{2}", t_clean))
    has_amount = bool(re.search(r"\d+[\,\.]\d{2}", t_clean))
    has_currency = bool(re.search(r"[\$€£]|SGD|OMR|HKD|CAD|EUR|USD", t_clean, re.IGNORECASE))

    # Keyword features
    t_lower = t_clean.lower()
    has_header_kw = any(kw in t_lower for kw in HEADER_KEYWORDS)
    has_footer_kw = any(kw in t_lower for kw in FOOTER_KEYWORDS)
    has_balance_kw = any(kw in t_lower for kw in BALANCE_KEYWORDS)

    return {
        "rel_y0": round(rel_y0, 3),
        "rel_x0": round(rel_x0, 3),
        "line_w": round(line_w, 3),
        "line_h": round(line_h, 2),
        "num_words": num_words,
        "digit_ratio": round(digit_ratio, 3),
        "upper_ratio": round(upper_ratio, 3),
        "starts_with_date": int(starts_with_date),
        "has_date": int(has_date),
        "has_amount": int(has_amount),
        "has_currency": int(has_currency),
        "has_header_kw": int(has_header_kw),
        "has_footer_kw": int(has_footer_kw),
        "has_balance_kw": int(has_balance_kw),
        "prev_label": prev_label or "NONE"
    }


class LineClassifier:
    """Scikit-learn based text line role classifier."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "data/models_cache/line_classifier.joblib"
        self.pipeline: Optional[Pipeline] = None
        self._load_or_train()

    def _load_or_train(self):
        if os.path.exists(self.model_path):
            try:
                self.pipeline = joblib.load(self.model_path)
                return
            except Exception:
                pass
        # Model not found or failed, train default
        self.train_default_model()

    def train_default_model(self):
        """Train classifier on representative synthetic banking document lines."""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        except Exception:
            pass
        
        # Synthetic representative training lines
        samples = [
            # TABLE_HEADER
            ("Date Description Withdrawal (-) Deposit (+) Balance", (40, 180, 530, 192), 595, 842, "TABLE_HEADER"),
            ("Post Date Trans Date Merchant Name or Transaction Description $ Amount", (30, 145, 500, 156), 612, 792, "TABLE_HEADER"),
            ("Date Interest Date Counterparty Description Amount", (40, 360, 520, 372), 595, 842, "TABLE_HEADER"),
            ("Date Transaction Details Deposit Withdrawal Balance", (40, 204, 530, 216), 595, 842, "TABLE_HEADER"),
            ("Détails Chèques et débits ($) Dépôts et crédits ($) Solde ($)", (40, 384, 520, 396), 595, 842, "TABLE_HEADER"),
            ("Transaction Date Value Date Particulars Chq No Debit Credit Balance", (40, 190, 540, 202), 595, 842, "TABLE_HEADER"),
            
            # TRANSACTION_START
            ("01/01/2025 Paynow from Corp Holdings 1,902.69 17,353.44", (40, 247, 526, 258), 595, 842, "TRANSACTION_START"),
            ("01/01/2025 Paynow Guardian Health 70.64 17,282.80", (40, 288, 526, 299), 595, 842, "TRANSACTION_START"),
            ("09/01 09/01 UBER TRIP 531.56", (30, 167, 500, 178), 612, 792, "TRANSACTION_START"),
            ("09/07 09/07 WHOLE FOODS MARKET 1,124.43", (30, 209, 500, 220), 612, 792, "TRANSACTION_START"),
            ("22 mei 22.05 SANNE BOS BIJSCHRIJVING 37,04 €", (40, 60, 520, 72), 595, 842, "TRANSACTION_START"),
            ("24 mei 24.05 Eneco DOORLOPENDE MACHTIGING -890,43 €", (40, 91, 520, 102), 595, 842, "TRANSACTION_START"),
            ("27 Jun FPS PAYMENT 7404351 TO: HKIRD 52,999.28", (40, 220, 530, 232), 595, 842, "TRANSACTION_START"),
            ("1 Jul FPS PAYMENT 1465378 TO: PARKnSHOP 12,977.92", (40, 250, 530, 262), 595, 842, "TRANSACTION_START"),
            ("21 janv. 25 UBER COURSE 45,50 $ 11 088,10 $", (40, 420, 520, 432), 595, 842, "TRANSACTION_START"),
            ("15/01/2025 15/01/2025 SALARY CREDIT PETROLEUM DEV 450.000 1,250.750", (40, 240, 540, 252), 595, 842, "TRANSACTION_START"),
            ("18/01/2025 18/01/2025 ATM CASH W/D MUSCAT MALL 50.000 1,200.750", (40, 260, 540, 272), 595, 842, "TRANSACTION_START"),

            # TRANSACTION_CONTINUATION
            ("PAYNOW TRANSFER 8373579", (113, 255, 250, 265), 595, 842, "TRANSACTION_CONTINUATION"),
            ("TO: Corp Holdings", (113, 264, 220, 274), 595, 842, "TRANSACTION_CONTINUATION"),
            ("P4583998QR", (113, 273, 180, 283), 595, 842, "TRANSACTION_CONTINUATION"),
            ("REF: 775648", (50, 180, 150, 190), 612, 792, "TRANSACTION_CONTINUATION"),
            ("Chevron station #0441 38.2gal premium 0.00", (50, 193, 300, 203), 612, 792, "TRANSACTION_CONTINUATION"),
            ("NL54VNXX1840427254", (40, 38, 200, 48), 595, 842, "TRANSACTION_CONTINUATION"),
            ("TO: HKIRD P6678346QR", (100, 230, 250, 240), 595, 842, "TRANSACTION_CONTINUATION"),
            ("TXN REF FT250150992384", (110, 250, 250, 260), 595, 842, "TRANSACTION_CONTINUATION"),

            # METADATA_HEADER
            ("SC Savings Account Account Number 2161-2777-1657", (40, 154, 350, 166), 595, 842, "METADATA_HEADER"),
            ("Transaction Details as at 31/01/2025", (40, 84, 280, 96), 595, 842, "METADATA_HEADER"),
            ("Account Name: Ahmed Al-Harthy", (40, 100, 250, 112), 595, 842, "METADATA_HEADER"),
            ("Account Number: 0315-01234567-001 IBAN: OM310000031501234567001", (40, 115, 450, 127), 595, 842, "METADATA_HEADER"),
            ("Branch: Muscat Main Branch Currency: OMR", (40, 130, 320, 142), 595, 842, "METADATA_HEADER"),
            ("HKD Current Account — 817-890692-838", (40, 100, 300, 112), 595, 842, "METADATA_HEADER"),

            # BALANCE_SUMMARY
            ("Balance Brought Forward SGD 15,450.75", (40, 224, 400, 235), 595, 842, "BALANCE_SUMMARY"),
            ("Balance Carried Forward in SGD: 2,181.67 2,002.15 15,271.23", (40, 741, 520, 752), 595, 842, "BALANCE_SUMMARY"),
            ("Solde D'ouverture 1 janvier 2025 10 750,00 $", (40, 259, 450, 270), 595, 842, "BALANCE_SUMMARY"),
            ("Solde De Fermeture 31 janvier 2025 = 11 133,60 $", (40, 299, 450, 310), 595, 842, "BALANCE_SUMMARY"),
            ("Opening Balance: 1,000.000 Closing Balance: 1,200.750", (40, 160, 480, 172), 595, 842, "BALANCE_SUMMARY"),
            ("Total Deposit Amount: HKD 533.79 Total Withdrawal Amount: HKD 24,749.67", (40, 575, 500, 586), 595, 842, "BALANCE_SUMMARY"),

            # NOISE_FOOTER
            ("With effect from 16 September 2024, selected clauses in Terms will be updated.", (40, 800, 550, 810), 595, 842, "NOISE_FOOTER"),
            ("Transaction Details as of 31/01/2025 Page 2 of 3", (40, 803, 500, 814), 595, 842, "NOISE_FOOTER"),
            ("This product is eligible for the Deposit Guarantee Scheme.", (40, 797, 500, 808), 595, 842, "NOISE_FOOTER"),
            ("SC_SOA_LOC_0216127771657_00012", (40, 819, 300, 829), 595, 842, "NOISE_FOOTER"),
            ("Outside the U.S.: 1-302-594-8200", (40, 780, 300, 790), 612, 792, "NOISE_FOOTER"),
            ("Please examine this statement within 14 days of receipt.", (40, 810, 500, 820), 595, 842, "NOISE_FOOTER")
        ]

        # Duplicate and perturb to expand dataset
        X_feats = []
        y_labels = []
        for text, bbox, pw, ph, label in samples:
            for shift_y in [-5.0, 0.0, 5.0]:
                adj_bbox = (bbox[0], max(0.0, bbox[1] + shift_y), bbox[2], min(ph, bbox[3] + shift_y))
                feat = extract_features_from_line(text, adj_bbox, pw, ph)
                X_feats.append(feat)
                y_labels.append(label)

        # Build pipeline
        self.pipeline = Pipeline([
            ("vectorizer", DictVectorizer(sparse=False)),
            ("classifier", RandomForestClassifier(n_estimators=50, random_state=42, max_depth=8))
        ])
        self.pipeline.fit(X_feats, y_labels)
        try:
            joblib.dump(self.pipeline, self.model_path)
        except Exception:
            pass

    def predict_role(
        self,
        text: str,
        bbox: Tuple[float, float, float, float],
        page_width: float,
        page_height: float,
        prev_label: Optional[str] = None
    ) -> str:
        """Classify a line role using the ML model, with heuristic fallback."""
        if self.pipeline is not None:
            feat = extract_features_from_line(text, bbox, page_width, page_height, prev_label)
            try:
                pred = self.pipeline.predict([feat])[0]
                return str(pred)
            except Exception:
                pass
        
        # Heuristic fallback (Baseline)
        return self._heuristic_predict(text, bbox, page_width, page_height)

    @staticmethod
    def _heuristic_predict(
        text: str,
        bbox: Tuple[float, float, float, float],
        page_width: float,
        page_height: float
    ) -> str:
        """Rule-based baseline classifier."""
        t_clean = text.strip()
        t_lower = t_clean.lower()
        rel_y = bbox[1] / page_height if page_height > 0 else 0.0

        if rel_y > 0.88 or any(kw in t_lower for kw in FOOTER_KEYWORDS):
            return "NOISE_FOOTER"
        if any(kw in t_lower for kw in BALANCE_KEYWORDS):
            return "BALANCE_SUMMARY"
        if any(kw in t_lower for kw in HEADER_KEYWORDS) and len(t_clean.split()) >= 3:
            return "TABLE_HEADER"
        if re.match(r"^(\d{1,2}[/\-\.]\d{1,2}|\d{1,2}\s+[a-zA-Z]{3})", t_clean):
            return "TRANSACTION_START"
        if any(kw in t_lower for kw in ["account number", "iban", "branch", "currency:"]):
            return "METADATA_HEADER"
        return "TRANSACTION_CONTINUATION"
