"""
Live Runtime API Verification Script for Bank Statement Table Extraction & Banking Analytics API.
Binds to local TCP socket, launches Uvicorn server in background, and performs end-to-end HTTP tests.
"""

import os
import sys
import time
import socket
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httpx
import uvicorn
from app.main import app

HOST = "127.0.0.1"
PORT = 8011  # dedicated verification port


class ServerThread(threading.Thread):
    def __init__(self, app, host, port):
        super().__init__(daemon=True)
        config = uvicorn.Config(app=app, host=host, port=port, log_level="warning")
        self.server = uvicorn.Server(config=config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


def wait_for_server(url: str, timeout: float = 10.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = httpx.get(url, timeout=1.0)
            if r.status_code == 200:
                return True
        except Exception:
            time.sleep(0.2)
    return False


def run_live_verification():
    print(f"Starting background Uvicorn server on http://{HOST}:{PORT}...")
    server_thread = ServerThread(app, HOST, PORT)
    server_thread.start()

    base_url = f"http://{HOST}:{PORT}"
    if not wait_for_server(f"{base_url}/health"):
        print("ERROR: Server failed to start within timeout.")
        server_thread.stop()
        sys.exit(1)

    print("Server is live. Executing end-to-end API verification suite...\n")

    client = httpx.Client(base_url=base_url, timeout=30.0)
    passed_checks = 0

    try:
        # Check 1: GET /health
        r = client.get("/health")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        health_data = r.json()
        assert health_data["status"] == "healthy"
        assert health_data["ml_line_classifier_loaded"] is True
        assert health_data["nlp_categorizer_loaded"] is True
        print(f"[PASS 1/7] GET /health -> Status: {health_data['status']}, Models loaded: True")
        passed_checks += 1

        # Check 2: GET /profiles
        r = client.get("/profiles")
        assert r.status_code == 200
        profiles_data = r.json()
        assert profiles_data["count"] >= 6
        assert any(p["id"] == "bank_muscat" for p in profiles_data["profiles"])
        print(f"[PASS 2/7] GET /profiles -> {profiles_data['count']} profiles registered (including Bank Muscat)")
        passed_checks += 1

        # Check 3: POST /extract (JSON) on bank_muscat_sample.pdf
        sample_pdf_path = "data/raw/bank_muscat_sample.pdf"
        with open(sample_pdf_path, "rb") as f:
            pdf_bytes = f.read()

        r = client.post(
            "/extract",
            files={"file": ("bank_muscat_sample.pdf", pdf_bytes, "application/pdf")},
            data={"profile": "auto", "output_format": "json"}
        )
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        extract_json = r.json()
        assert extract_json["metadata"]["bank"] == "Bank Muscat"
        assert extract_json["metadata"]["currency"] == "OMR"
        assert extract_json["metadata"]["transaction_count"] == 7
        assert extract_json["validation"]["reconciled"] is True
        print(f"[PASS 3/7] POST /extract (JSON) -> Bank Muscat extracted 7 txns, reconciled: True")
        passed_checks += 1

        # Check 4: POST /extract (CSV) on bank_muscat_sample.pdf
        r = client.post(
            "/extract",
            files={"file": ("bank_muscat_sample.pdf", pdf_bytes, "application/pdf")},
            data={"profile": "auto", "output_format": "csv"}
        )
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/csv")
        assert "SALARY CREDIT" in r.text
        print(f"[PASS 4/7] POST /extract (CSV) -> Valid CSV response generated ({len(r.text.splitlines())} lines)")
        passed_checks += 1

        # Check 5: POST /categorize (scikit-learn fast path)
        cat_payload = {
            "descriptions": [
                "SALARY CREDIT MINISTRY OF FINANCE REF99281",
                "ATM CASH W/D MUSCAT CITY CENTRE",
                "LULU HYPERMARKET POS PURCHASE"
            ],
            "use_transformers": False
        }
        r = client.post("/categorize", json=cat_payload)
        assert r.status_code == 200
        cat_json = r.json()
        assert cat_json["model_used"] == "scikit-learn TF-IDF Classifier"
        assert cat_json["results"][0]["category"] == "INCOME_SALARY"
        assert cat_json["results"][1]["category"] == "ATM_CASH"
        assert cat_json["results"][2]["category"] == "MERCHANT_POS"
        print(f"[PASS 5/7] POST /categorize (scikit-learn) -> {cat_json['model_used']}, 3/3 accurate")
        passed_checks += 1

        # Check 6: POST /categorize (Hugging Face Transformer path)
        cat_payload_tf = {
            "descriptions": ["SALARY CREDIT MINISTRY OF FINANCE REF99281"],
            "use_transformers": True
        }
        r = client.post("/categorize", json=cat_payload_tf)
        assert r.status_code == 200
        cat_json_tf = r.json()
        assert "HuggingFace Transformers" in cat_json_tf["model_used"]
        print(f"[PASS 6/7] POST /categorize (Transformers) -> {cat_json_tf['model_used']}, output: {cat_json_tf['results'][0]['category']}")
        passed_checks += 1

        # Check 7: Security - Magic Bytes Validation
        r = client.post(
            "/extract",
            files={"file": ("fake.pdf", b"INVALID_HEADER_DATA_12345", "application/pdf")},
            data={"profile": "auto"}
        )
        assert r.status_code == 400
        assert "file header does not begin with '%PDF-'" in r.json()["detail"]
        print(f"[PASS 7/7] Security: Corrupt PDF magic byte payload correctly rejected with HTTP 400")
        passed_checks += 1

    finally:
        server_thread.stop()
        time.sleep(0.5)

    print(f"\n=================================================================================")
    print(f"LIVE RUNTIME API VERIFICATION SUCCESSFUL: {passed_checks}/7 CHECKS PASSED")
    print(f"=================================================================================\n")


if __name__ == "__main__":
    run_live_verification()
