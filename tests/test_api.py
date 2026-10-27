"""
Tests for FastAPI REST API endpoints using Starlette/FastAPI TestClient.
"""

import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["ml_line_classifier_loaded"] is True
    assert data["nlp_categorizer_loaded"] is True
    assert "bank_muscat" in data["supported_profiles"]


def test_profiles_endpoint():
    response = client.get("/profiles")
    assert response.status_code == 200
    data = response.json()
    assert "profiles" in data
    assert any(p["id"] == "bank_muscat" for p in data["profiles"])


def test_categorize_endpoint():
    payload = {
        "descriptions": [
            "SALARY CREDIT MINISTRY OF FINANCE",
            "ATM CASH W/D MUSCAT CITY CENTRE",
            "UBER TRIP RIDE TO WORK"
        ],
        "use_transformers": False
    }
    response = client.post("/categorize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 3
    assert data["results"][0]["category"] == "INCOME_SALARY"
    assert data["results"][1]["category"] == "ATM_CASH"
    assert data["results"][2]["category"] == "MERCHANT_POS"
    assert data["model_used"] == "scikit-learn TF-IDF Classifier"


def test_categorize_endpoint_transformers_error_handling():
    """Verify that when use_transformers is requested without loaded weights, failure is explicit (no silent false claim)."""
    from app.api.endpoints import extractor_service
    orig_model = extractor_service.nlp_categorizer.hf_model_name
    extractor_service.nlp_categorizer.hf_model_name = "invalid-unloaded-transformer-model"
    extractor_service.nlp_categorizer.hf_pipeline = None

    try:
        payload = {
            "descriptions": ["SALARY CREDIT MINISTRY OF FINANCE"],
            "use_transformers": True
        }
        response = client.post("/categorize", json=payload)
        assert response.status_code == 503
        data = response.json()
        assert "Hugging Face Transformer pipeline unavailable" in data["detail"]
        assert "use_transformers=false" in data["detail"]
    finally:
        extractor_service.nlp_categorizer.hf_model_name = orig_model
        extractor_service.nlp_categorizer.hf_pipeline = None


def test_extract_endpoint_json():
    pdf_path = "data/raw/bank_muscat_sample.pdf"
    if not os.path.exists(pdf_path):
        from scripts.generate_bank_muscat_sample import generate_bank_muscat_pdf
        generate_bank_muscat_pdf(pdf_path)

    with open(pdf_path, "rb") as f:
        response = client.post(
            "/extract",
            files={"file": ("bank_muscat_sample.pdf", f, "application/pdf")},
            data={"profile": "auto", "output_format": "json"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["bank"] == "Bank Muscat"
    assert data["metadata"]["currency"] == "OMR"
    assert data["metadata"]["transaction_count"] == 7
    assert data["validation"]["reconciled"] is True


def test_extract_endpoint_csv():
    pdf_path = "data/raw/bank_muscat_sample.pdf"
    with open(pdf_path, "rb") as f:
        response = client.post(
            "/extract",
            files={"file": ("bank_muscat_sample.pdf", f, "application/pdf")},
            data={"profile": "auto", "output_format": "csv"}
        )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "date,value_date,description,amount,direction" in response.text
    assert "SALARY CREDIT" in response.text


def test_extract_endpoint_benchmark_format():
    pdf_path = "data/bankstatemently_benchmark/datasets/basic/bsb-001/bsb-001-statement.pdf"
    if not os.path.exists(pdf_path):
        pytest.skip("Benchmark statement not available")

    with open(pdf_path, "rb") as f:
        response = client.post(
            "/extract",
            files={"file": ("bsb-001-statement.pdf", f, "application/pdf")},
            data={"profile": "auto", "output_format": "benchmark"}
        )
    assert response.status_code == 200
    data = response.json()
    assert "contentHash" in data
    assert "transactions" in data
    assert len(data["transactions"]) == 12
    # Verify originalData exists as required by benchmark schema
    assert "originalData" in data["transactions"][0]


def test_extract_invalid_file_extension():
    response = client.post(
        "/extract",
        files={"file": ("statement.txt", b"plain text content", "text/plain")}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_extract_empty_file():
    response = client.post(
        "/extract",
        files={"file": ("empty.pdf", b"", "application/pdf")}
    )
    assert response.status_code == 400
    assert "Uploaded file is empty" in response.json()["detail"]


def test_extract_invalid_pdf_magic_bytes():
    """Verify that files ending in .pdf but lacking '%PDF-' magic bytes are rejected."""
    response = client.post(
        "/extract",
        files={"file": ("corrupt.pdf", b"NOT_A_REAL_PDF_HEADER_DATA", "application/pdf")}
    )
    assert response.status_code == 400
    assert "file header does not begin with '%PDF-'" in response.json()["detail"]


def test_api_key_authentication_enforcement(monkeypatch):
    """Verify X-API-Key authentication behavior when API_KEY is set."""
    test_key = "test-secret-banking-key-987"
    monkeypatch.setenv("API_KEY", test_key)

    # 1. Missing key -> 401
    payload = {"descriptions": ["SALARY CREDIT MINISTRY OF FINANCE"], "use_transformers": False}
    resp_no_key = client.post("/categorize", json=payload)
    assert resp_no_key.status_code == 401
    assert "Invalid or missing API key" in resp_no_key.json()["detail"]

    # 2. Invalid key -> 401
    resp_bad_key = client.post("/categorize", json=payload, headers={"X-API-Key": "wrong-key"})
    assert resp_bad_key.status_code == 401

    # 3. Valid key -> 200
    resp_valid_key = client.post("/categorize", json=payload, headers={"X-API-Key": test_key})
    assert resp_valid_key.status_code == 200
    assert resp_valid_key.json()["results"][0]["category"] == "INCOME_SALARY"
