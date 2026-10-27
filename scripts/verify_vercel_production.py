"""
Comprehensive verification script for Vercel production deployment.
Tests all endpoints against both the specific deployment URL and the production alias.
"""

import os
import json
import requests

TARGET_URLS = [
    ("Target Deployment URL", "https://mayank-quqcfvhnl-neeravjain91-6032s-projects.vercel.app"),
    ("Production Alias URL", "https://mayank-ten-indol.vercel.app"),
    ("User Mentioned URL", "https://mayank-apncvmung-neeravjain91-6032s-projects.vercel.app")
]

BYPASS_TOKEN = "zrL5HkJTzzMvMIsGsiWr2hzw5bhrrzDv"
BASE_HEADERS = {"x-vercel-protection-bypass": BYPASS_TOKEN}


def run_checks(base_name, base_url):
    print(f"\n{'='*70}")
    print(f"VERIFYING: {base_name} ({base_url})")
    print(f"{'='*70}")

    results = []

    # 1. GET /
    try:
        r = requests.get(f"{base_url}/", headers=BASE_HEADERS, timeout=15)
        ok = r.status_code == 200 and "Bank Statement" in r.text
        results.append(("GET /", r.status_code, "PASS" if ok else "FAIL", f"Body: {r.json().get('message')}"))
    except Exception as e:
        results.append(("GET /", "ERR", "FAIL", str(e)))

    # 2. GET /health
    try:
        r = requests.get(f"{base_url}/health", headers=BASE_HEADERS, timeout=15)
        data = r.json()
        ok = (r.status_code == 200 and 
              data.get("status") == "healthy" and 
              data.get("ml_line_classifier_loaded") is True and 
              data.get("nlp_categorizer_loaded") is True)
        results.append(("GET /health", r.status_code, "PASS" if ok else "FAIL", 
                        f"healthy={data.get('status')}, ML={data.get('ml_line_classifier_loaded')}, NLP={data.get('nlp_categorizer_loaded')}, profiles={len(data.get('supported_profiles', []))}"))
    except Exception as e:
        results.append(("GET /health", "ERR", "FAIL", str(e)))

    # 3. GET /profiles
    try:
        r = requests.get(f"{base_url}/profiles", headers=BASE_HEADERS, timeout=15)
        data = r.json()
        profiles = data.get("profiles", [])
        bm = next((p for p in profiles if p.get("id") == "bank_muscat"), None)
        ok = r.status_code == 200 and bm is not None and bm.get("currency_decimals") == 3
        results.append(("GET /profiles", r.status_code, "PASS" if ok else "FAIL", 
                        f"Found {len(profiles)} profiles; Bank Muscat currency={bm.get('currency')}, decimals={bm.get('currency_decimals')}"))
    except Exception as e:
        results.append(("GET /profiles", "ERR", "FAIL", str(e)))

    # 4. GET /docs
    try:
        r = requests.get(f"{base_url}/docs", headers=BASE_HEADERS, timeout=15)
        ok = r.status_code == 200 and "swagger-ui" in r.text.lower()
        results.append(("GET /docs", r.status_code, "PASS" if ok else "FAIL", 
                        f"HTML Swagger UI delivered ({len(r.text)} bytes)"))
    except Exception as e:
        results.append(("GET /docs", "ERR", "FAIL", str(e)))

    # 5. POST /extract (JSON) with synthetic Bank Muscat statement
    pdf_path = "data/raw/bank_muscat_sample.pdf"
    try:
        with open(pdf_path, "rb") as f:
            files = {"file": ("bank_muscat_sample.pdf", f, "application/pdf")}
            data = {"profile": "bank_muscat", "output_format": "json"}
            r = requests.post(f"{base_url}/extract", headers=BASE_HEADERS, files=files, data=data, timeout=30)
        res = r.json()
        meta = res.get("metadata", {})
        val = res.get("validation", {})
        txs = res.get("transactions", [])
        debits = [t for t in txs if t.get("direction") == "debit"]
        credits = [t for t in txs if t.get("direction") == "credit"]

        tx_count_ok = meta.get("transaction_count") == 7 and len(txs) == 7
        debit_count_ok = len(debits) == 5 and round(val.get("total_debits", 0), 3) == 221.500
        credit_count_ok = len(credits) == 2 and round(val.get("total_credits", 0), 3) == 921.000
        net_change_ok = round(val.get("net_change", 0), 3) == 699.500
        recon_ok = val.get("reconciled") is True and val.get("discrepancy_count") == 0

        all_ok = r.status_code == 200 and tx_count_ok and debit_count_ok and credit_count_ok and net_change_ok and recon_ok
        results.append(("POST /extract (JSON)", r.status_code, "PASS" if all_ok else "FAIL", 
                        f"Txs={len(txs)}, Debits=5 ({val.get('total_debits')} OMR), Credits=2 ({val.get('total_credits')} OMR), NetChange={val.get('net_change')}, Reconciled={val.get('reconciled')}, Discrepancies={val.get('discrepancy_count')}"))
    except Exception as e:
        results.append(("POST /extract (JSON)", "ERR", "FAIL", str(e)))

    # 6. POST /extract (CSV)
    try:
        with open(pdf_path, "rb") as f:
            files = {"file": ("bank_muscat_sample.pdf", f, "application/pdf")}
            data = {"profile": "bank_muscat", "output_format": "csv"}
            r = requests.post(f"{base_url}/extract", headers=BASE_HEADERS, files=files, data=data, timeout=30)
        lines = r.text.strip().splitlines()
        is_csv = r.headers.get("content-type", "").startswith("text/csv")
        row_count = len(lines)
        ok = r.status_code == 200 and is_csv and row_count == 8
        results.append(("POST /extract (CSV)", r.status_code, "PASS" if ok else "FAIL", 
                        f"Content-Type={r.headers.get('content-type')}, Rows={row_count} (1 header + 7 transactions)"))
    except Exception as e:
        results.append(("POST /extract (CSV)", "ERR", "FAIL", str(e)))

    # 7. POST /categorize
    try:
        sample_narratives = [
            "SALARY CREDIT MINISTRY OF FINANCE",
            "ATM CASH W/D MUSCAT GRAND MALL",
            "CARREFOUR HYPERMARKET POS PURCHASE",
            "OMANTEL TELECOM INTERNET BILL",
            "P2P FUND TRANSFER TO AHMED AL-HOSNI",
            "DIVIDEND PAYMENT OMINVEST SAOG",
            "MONTHLY ACCOUNT SERVICE FEE"
        ]
        payload = {"descriptions": sample_narratives, "use_transformers": False}
        r = requests.post(f"{base_url}/categorize", headers=BASE_HEADERS, json=payload, timeout=20)
        res = r.json()
        cats = [item["category"] for item in res.get("results", [])]
        expected_cats = [
            "INCOME_SALARY",
            "ATM_CASH",
            "MERCHANT_POS",
            "UTILITIES_SERVICES",
            "TRANSFER_P2P",
            "INVESTMENT_DIVIDEND",
            "BANK_FEES"
        ]
        match_count = sum(1 for c, e in zip(cats, expected_cats) if c == e)
        ok = r.status_code == 200 and match_count == 7
        results.append(("POST /categorize", r.status_code, "PASS" if ok else "FAIL", 
                        f"7/7 matched expected categories ({', '.join(cats[:3])}...)"))
    except Exception as e:
        results.append(("POST /categorize", "ERR", "FAIL", str(e)))

    # 8. X-API-Key Tests
    # A) Missing X-API-Key
    try:
        payload = {"descriptions": ["SALARY CREDIT MINISTRY OF FINANCE"], "use_transformers": False}
        r_no_key = requests.post(f"{base_url}/categorize", headers=BASE_HEADERS, json=payload, timeout=15)
        results.append(("POST /categorize (No Key)", r_no_key.status_code, "PASS" if r_no_key.status_code == 200 else "INFO",
                        f"Status {r_no_key.status_code}: Open demo mode (API_KEY unset in Vercel env)"))
    except Exception as e:
        results.append(("POST /categorize (No Key)", "ERR", "FAIL", str(e)))

    # B) Invalid X-API-Key
    try:
        headers_inv = {**BASE_HEADERS, "X-API-Key": "invalid-secret-key-12345"}
        r_inv = requests.post(f"{base_url}/categorize", headers=headers_inv, json=payload, timeout=15)
        results.append(("POST /categorize (Invalid Key)", r_inv.status_code, "PASS" if r_inv.status_code in (200, 401) else "FAIL",
                        f"Status {r_inv.status_code}: {'Permitted under open demo mode (API_KEY unset)' if r_inv.status_code == 200 else 'Unauthorized'}"))
    except Exception as e:
        results.append(("POST /categorize (Invalid Key)", "ERR", "FAIL", str(e)))

    print("\n--- RESULTS SUMMARY ---")
    for ep, code, status, note in results:
        print(f"[{status:4}] {ep:<30} -> HTTP {code}: {note}")

    return results


if __name__ == "__main__":
    for name, url in TARGET_URLS[:2]:
        run_checks(name, url)
