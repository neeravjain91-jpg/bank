"""
Verification script for live Vercel deployment of Bank Statement Table Extraction & Banking Analytics
Production URL: https://mayank-ten-indol.vercel.app
"""
import sys
import json
import requests

BASE_URL = "https://mayank-ten-indol.vercel.app"
BYPASS_TOKEN = "zrL5HkJTzzMvMIsGsiWr2hzw5bhrrzDv"
HEADERS = {"x-vercel-protection-bypass": BYPASS_TOKEN}

def test_root():
    print("\n--- 1. Testing GET / ---")
    r = requests.get(f"{BASE_URL}/", headers=HEADERS, timeout=15)
    print(f"Status: {r.status_code}")
    print(f"Body: {json.dumps(r.json(), indent=2)}")
    assert r.status_code == 200
    assert "Bank Statement" in r.json().get("message", "")

def test_health():
    print("\n--- 2. Testing GET /health ---")
    r = requests.get(f"{BASE_URL}/health", headers=HEADERS, timeout=15)
    print(f"Status: {r.status_code}")
    print(f"Body: {json.dumps(r.json(), indent=2)}")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert data["ml_line_classifier_loaded"] is True
    assert data["nlp_categorizer_loaded"] is True

def test_profiles():
    print("\n--- 3. Testing GET /profiles ---")
    r = requests.get(f"{BASE_URL}/profiles", headers=HEADERS, timeout=15)
    print(f"Status: {r.status_code}")
    profiles = r.json()
    print(f"Profiles count: {len(profiles.get('profiles', []))}")
    bank_muscat_found = any(p.get("id") == "bank_muscat" for p in profiles.get("profiles", []))
    print(f"Bank Muscat profile present: {bank_muscat_found}")
    assert r.status_code == 200
    assert bank_muscat_found

def test_categorize():
    print("\n--- 4. Testing POST /categorize ---")
    payload = {
        "descriptions": [
            "SALARY CREDIT MINISTRY OF FINANCE",
            "ATM CASH W/D MUSCAT MALL",
            "CARREFOUR HYPERMARKET POS PURCHASE",
            "OMANTEL TELECOM INTERNET BILL",
            "P2P FUND TRANSFER TO AHMED AL-HOSNI",
            "DIVIDEND PAYMENT OMINVEST SAOG",
            "MONTHLY ACCOUNT SERVICE FEE"
        ],
        "use_transformers": False
    }
    r = requests.post(f"{BASE_URL}/categorize", headers=HEADERS, json=payload, timeout=20)
    print(f"Status: {r.status_code}")
    res = r.json()
    results = res.get("results", [])
    print(f"Model used: {res.get('model_used')}")
    print(f"Classifications count: {len(results)}")
    for item in results:
        print(f"  [{item['category']}] (conf: {item['confidence']:.2f}, channel: {item.get('channel')}) -> {item['description']}")
    assert r.status_code == 200
    assert len(results) == 7

def test_extract_json():
    print("\n--- 5. Testing POST /extract (JSON) with bank_muscat_sample.pdf ---")
    pdf_path = "data/raw/bank_muscat_sample.pdf"
    with open(pdf_path, "rb") as f:
        files = {"file": ("bank_muscat_sample.pdf", f, "application/pdf")}
        data = {"profile": "bank_muscat", "output_format": "json"}
        r = requests.post(f"{BASE_URL}/extract", headers=HEADERS, files=files, data=data, timeout=30)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        res = r.json()
        meta = res.get("metadata", {})
        val = res.get("validation", {})
        txs = res.get("transactions", [])
        print(f"Filename: {meta.get('file_name')}")
        print(f"Profile: {meta.get('profile_used')}")
        print(f"Extraction method: {meta.get('extraction_method')}")
        print(f"Extracted transactions: {meta.get('transaction_count')}")
        print(f"Reconciled: {val.get('reconciled')}")
        print(f"Total Debits: {val.get('total_debits')}")
        print(f"Total Credits: {val.get('total_credits')}")
        print(f"Net Change: {val.get('net_change')}")
        print(f"Discrepancies: {val.get('discrepancy_count')}")
        print("Sample extracted transactions:")
        for tx in txs[:3]:
            print(f"  {tx['date']} | {tx['description'][:35]} | DR: {tx.get('debit')} | CR: {tx.get('credit')} | BAL: {tx.get('balance')}")
        assert meta.get("transaction_count", 0) > 0
        assert len(txs) > 0
    else:
        print(f"Error: {r.text}")
        assert False, f"Extraction failed with status {r.status_code}"

def test_extract_csv():
    print("\n--- 6. Testing POST /extract (CSV) with bank_muscat_sample.pdf ---")
    pdf_path = "data/raw/bank_muscat_sample.pdf"
    with open(pdf_path, "rb") as f:
        files = {"file": ("bank_muscat_sample.pdf", f, "application/pdf")}
        data = {"profile": "bank_muscat", "output_format": "csv"}
        r = requests.post(f"{BASE_URL}/extract", headers=HEADERS, files=files, data=data, timeout=30)
    print(f"Status: {r.status_code}")
    print(f"Content-Type: {r.headers.get('content-type')}")
    lines = r.text.strip().splitlines()
    print(f"CSV header: {lines[0] if lines else 'NONE'}")
    print(f"Total lines: {len(lines)}")
    assert r.status_code == 200
    assert "date,description,debit,credit,balance" in lines[0] or "date" in lines[0]

def test_invalid_file_rejection():
    print("\n--- 7. Testing security/validation rejection for non-PDF file ---")
    files = {"file": ("malicious.exe", b"NOT_A_REAL_PDF_HEADER", "application/octet-stream")}
    data = {"profile": "generic"}
    r = requests.post(f"{BASE_URL}/extract", headers=HEADERS, files=files, data=data, timeout=15)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    assert r.status_code in (400, 422)

if __name__ == "__main__":
    try:
        test_root()
        test_health()
        test_profiles()
        test_categorize()
        test_extract_json()
        test_extract_csv()
        test_invalid_file_rejection()
        print("\n========================================================")
        print(">>> ALL 7 LIVE VERCEL ENDPOINT CHECKS PASSED PERFECTLY! <<<")
        print("========================================================")
    except Exception as e:
        print(f"\nVerification FAILED with exception: {e}")
        sys.exit(1)
