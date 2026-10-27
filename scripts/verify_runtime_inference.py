import os
import sys
import time
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath("."))

os.environ["HF_HUB_DISABLE_XET"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from fastapi.testclient import TestClient
from app.main import app
from app.models.nlp_categorizer import NLPCategorizer, CATEGORIES

# Representative synthetic banking narratives specified by the directive
TEST_NARRATIVES = [
    ("Salary credit", "SALARY CREDIT PETROLEUM DEV OMAN EMPLOYEE ID PDO-99120", "INCOME_SALARY"),
    ("ATM cash withdrawal", "ATM CASH WITHDRAWAL MUSCAT GRAND MALL ATM-9921", "ATM_CASH"),
    ("Merchant POS transaction", "POS PURCHASE LULU HYPERMARKET BAUSHER STORE-4412", "MERCHANT_POS"),
    ("Utility bill payment", "UTILITY BILL PAYMENT OMANTEL ACCOUNT 968-2419-01", "UTILITIES_SERVICES"),
    ("Person-to-person transfer", "FUNDS TRANSFER TO SALIM AL-BALUSHI FAMILY SUPPORT REF 99214", "TRANSFER_P2P"),
    ("Investment dividend", "DIVIDEND CREDIT OMINVEST SECURITIES ANNUAL DISTRIBUTION 2024", "INVESTMENT_DIVIDEND"),
    ("Bank fee", "MONTHLY SERVICE FEE ACCOUNT MAINTENANCE CHG001", "BANK_FEES"),
]

def run_transformer_verification():
    print("=" * 90)
    print("STAGE 1: VERIFYING ACTUAL TRANSFORMER MODEL LOADING & INFERENCE")
    print("=" * 90)
    
    categorizer = NLPCategorizer()
    model_name = categorizer.hf_model_name
    print(f"Target Transformer Model: {model_name}")
    
    t0 = time.time()
    try:
        categorizer.load_transformers_pipeline()
        load_time = time.time() - t0
        print(f"[SUCCESS] Model and tokenizer loaded successfully in {load_time:.2f}s on CPU.")
    except Exception as e:
        print(f"[FAILED] Could not load model: {type(e).__name__}: {e}")
        return False, str(e)
    
    print("\nExecuting Transformer inference across representative synthetic banking narratives:")
    print("-" * 90)
    print(f"{'Narrative Type':<25} | {'Raw Narration':<35} | {'Predicted':<20} | {'Score':<8} | {'Latency':<8}")
    print("-" * 90)
    
    results = []
    total_time = 0.0
    for n_type, desc, expected in TEST_NARRATIVES:
        t_start = time.time()
        cat, score, entities = categorizer.categorize(desc, use_transformers=True)
        t_elapsed = (time.time() - t_start) * 1000  # ms
        total_time += t_elapsed
        
        # Validation checks
        assert cat in CATEGORIES, f"Category '{cat}' not in {CATEGORIES}"
        assert 0.0 <= score <= 1.0, f"Score {score} not a valid probability"
        assert not (score != score), "Score is NaN"
        
        trunc_desc = (desc[:32] + "...") if len(desc) > 35 else desc
        print(f"{n_type:<25} | {trunc_desc:<35} | {cat:<20} | {score:<8.4f} | {t_elapsed:<6.1f} ms")
        results.append({
            "type": n_type,
            "description": desc,
            "expected_category": expected,
            "predicted_category": cat,
            "confidence": score,
            "latency_ms": round(t_elapsed, 1),
            "entities": entities
        })
        
    avg_latency = total_time / len(TEST_NARRATIVES)
    print("-" * 90)
    print(f"Average CPU Inference Latency: {avg_latency:.1f} ms per transaction")
    
    print("\n" + "=" * 90)
    print("STAGE 2: VERIFYING FASTAPI /categorize ENDPOINT WITH TRANSFORMERS")
    print("=" * 90)
    client = TestClient(app)
    
    api_resp = client.post("/categorize", json={
        "descriptions": ["SALARY CREDIT PETROLEUM DEV OMAN EMPLOYEE ID PDO-99120"],
        "use_transformers": True
    })
    
    print(f"API Response Status Code: {api_resp.status_code}")
    print(f"API Response Body: {json.dumps(api_resp.json(), indent=2)}")
    
    assert api_resp.status_code == 200, f"Expected 200, got {api_resp.status_code}"
    api_data = api_resp.json()
    assert "HuggingFace Transformers" in api_data["model_used"], f"Incorrect model_used: {api_data['model_used']}"
    assert api_data["model_used"] == f"HuggingFace Transformers ({model_name})", f"Mismatch in model attribution: {api_data['model_used']}"
    assert len(api_data["results"]) == 1
    res0 = api_data["results"][0]
    assert res0["category"] in CATEGORIES
    assert 0.0 <= res0["confidence"] <= 1.0
    print("[SUCCESS] API endpoint correctly executed Transformer pipeline and reported exact model!")

    print("\n" + "=" * 90)
    print("STAGE 3: VERIFYING FASTAPI /categorize ENDPOINT WITH SCIKIT-LEARN (DEFAULT)")
    print("=" * 90)
    api_skl = client.post("/categorize", json={
        "descriptions": ["SALARY CREDIT PETROLEUM DEV OMAN EMPLOYEE ID PDO-99120"],
        "use_transformers": False
    })
    print(f"scikit-learn Response Status Code: {api_skl.status_code}")
    print(f"scikit-learn Response Body: {json.dumps(api_skl.json(), indent=2)}")
    assert api_skl.status_code == 200
    assert "scikit-learn" in api_skl.json()["model_used"]
    print("[SUCCESS] API cleanly distinguishes scikit-learn vs Transformers without false claims!")

    print("\n" + "=" * 90)
    print("STAGE 4: VERIFYING FAILURE HANDLING WHEN TRANSFORMER WEIGHTS ARE UNAVAILABLE")
    print("=" * 90)
    # Direct class failure test
    err_cat = NLPCategorizer()
    err_cat.hf_model_name = "test-offline-error"
    err_cat.hf_pipeline = None
    try:
        err_cat.categorize("SALARY CREDIT", use_transformers=True)
        assert False, "Expected RuntimeError was not raised!"
    except RuntimeError as ex:
        print(f"[SUCCESS] Caught expected RuntimeError in NLPCategorizer: {ex}")

    # API endpoint 503 test
    from app.api.endpoints import extractor_service
    orig_pipe = extractor_service.nlp_categorizer.hf_pipeline
    orig_model = extractor_service.nlp_categorizer.hf_model_name
    
    try:
        extractor_service.nlp_categorizer.hf_pipeline = None
        extractor_service.nlp_categorizer.hf_model_name = "test-offline-error"
        
        err_api_resp = client.post("/categorize", json={
            "descriptions": ["SALARY CREDIT PETROLEUM DEV OMAN EMPLOYEE ID PDO-99120"],
            "use_transformers": True
        })
        print(f"Error Test Status Code: {err_api_resp.status_code}")
        print(f"Error Test Response: {err_api_resp.json()}")
        assert err_api_resp.status_code == 503, f"Expected 503, got {err_api_resp.status_code}"
        assert "503" in str(err_api_resp.status_code)
        assert "unavailable" in err_api_resp.json()["detail"].lower()
        print("[SUCCESS] API returned HTTP 503 with helpful remediation instructions.")
        
        # Verify fallback to scikit-learn works even when transformers are broken
        ok_api_resp = client.post("/categorize", json={
            "descriptions": ["SALARY CREDIT PETROLEUM DEV OMAN EMPLOYEE ID PDO-99120"],
            "use_transformers": False
        })
        assert ok_api_resp.status_code == 200
        assert "scikit-learn" in ok_api_resp.json()["model_used"]
        print("[SUCCESS] Ordinary scikit-learn classification continues working seamlessly.")
    finally:
        extractor_service.nlp_categorizer.hf_pipeline = orig_pipe
        extractor_service.nlp_categorizer.hf_model_name = orig_model

    print("\n[SUCCESS] ALL RUNTIME TRANSFORMER VERIFICATION STAGES PASSED!")
    return True, results

if __name__ == "__main__":
    success, details = run_transformer_verification()
    if not success:
        sys.exit(1)
