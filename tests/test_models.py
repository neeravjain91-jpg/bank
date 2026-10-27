"""
Unit tests for Machine Learning and NLP classification models.
"""

import pytest
from app.models.line_classifier import LineClassifier, extract_features_from_line
from app.models.nlp_categorizer import NLPCategorizer, extract_semantic_entities


def test_line_feature_extraction():
    text = "01/01/2025 Paynow from 1,902.69 17,353.44"
    bbox = (40.0, 247.0, 526.0, 258.0)
    feats = extract_features_from_line(text, bbox, 595.0, 842.0)
    assert feats["has_date"] == 1
    assert feats["starts_with_date"] == 1
    assert feats["has_amount"] == 1
    assert feats["num_words"] > 3


def test_line_classifier_predictions():
    clf = LineClassifier()
    
    # Table header
    role_hdr = clf.predict_role(
        "Date Description Withdrawal (-) Deposit (+) Balance",
        (40.0, 180.0, 530.0, 192.0),
        595.0, 842.0
    )
    assert role_hdr == "TABLE_HEADER"

    # Transaction start
    role_txn = clf.predict_role(
        "01/01/2025 Paynow Guardian Health 70.64 17,282.80",
        (40.0, 288.0, 526.0, 299.0),
        595.0, 842.0
    )
    assert role_txn == "TRANSACTION_START"

    # Transaction continuation
    role_cont = clf.predict_role(
        "PAYNOW TO 9547491",
        (113.0, 297.0, 250.0, 307.0),
        595.0, 842.0
    )
    assert role_cont == "TRANSACTION_CONTINUATION"


def test_nlp_entity_extraction():
    entities1 = extract_semantic_entities("Paynow from Corp Holdings PAYNOW TRANSFER 8373579")
    assert entities1["channel"] == "PAYNOW"
    assert entities1["reference_id"] is not None

    entities2 = extract_semantic_entities("ATM CASH WITHDRAWAL MUSCAT GRAND MALL")
    assert entities2["channel"] == "ATM"

    entities3 = extract_semantic_entities("POS PURCHASE LULU HYPERMARKET POS-88412")
    assert entities3["channel"] == "POS"


def test_nlp_categorizer_predictions():
    categorizer = NLPCategorizer()
    
    cat, conf, _ = categorizer.categorize("SALARY CREDIT - ACME PTE LTD")
    assert cat == "INCOME_SALARY"
    assert conf > 0.0

    cat2, conf2, _ = categorizer.categorize("ATM WITHDRAWAL MUSCAT MALL")
    assert cat2 == "ATM_CASH"

    cat3, conf3, _ = categorizer.categorize("STARBUCKS COFFEE DoorDash NYC")
    assert cat3 == "MERCHANT_POS"


def test_regression_merchant_pos_classification():
    """Regression test: POS purchase at Lulu Hypermarket must NOT be misclassified as INVESTMENT_DIVIDEND."""
    categorizer = NLPCategorizer()
    desc = "POS PURCHASE LULU HYPERMARKET BAUSHER STORE-4412"
    
    # 1. Scikit-learn production classifier
    cat_skl, conf_skl, _ = categorizer.categorize(desc, use_transformers=False)
    assert cat_skl == "MERCHANT_POS"
    assert conf_skl > 0.0

    # 2. Transformer zero-shot classifier
    cat_hf, conf_hf, _ = categorizer.categorize(desc, use_transformers=True)
    assert cat_hf == "MERCHANT_POS"
    assert conf_hf > 0.50


def test_regression_bank_fee_classification():
    """Regression test: Monthly service fee must NOT be misclassified as UTILITIES_SERVICES."""
    categorizer = NLPCategorizer()
    desc = "MONTHLY SERVICE FEE ACCOUNT MAINTENANCE CHG001"
    
    # 1. Scikit-learn production classifier
    cat_skl, conf_skl, _ = categorizer.categorize(desc, use_transformers=False)
    assert cat_skl == "BANK_FEES"
    assert conf_skl > 0.0

    # 2. Transformer zero-shot classifier
    cat_hf, conf_hf, _ = categorizer.categorize(desc, use_transformers=True)
    assert cat_hf == "BANK_FEES"
    assert conf_hf > 0.50


def test_nlp_categorizer_transformer_unavailability_handling():
    """Verify that when use_transformers=True is called without loaded pipeline, it raises RuntimeError rather than silently falling back."""
    categorizer = NLPCategorizer()
    categorizer.hf_pipeline = None
    categorizer.hf_model_name = "invalid-unloaded-transformer-model"
    with pytest.raises(RuntimeError) as exc_info:
        categorizer.categorize("SALARY CREDIT - ACME PTE LTD", use_transformers=True)
    assert "Failed to load Hugging Face Transformer model" in str(exc_info.value)
