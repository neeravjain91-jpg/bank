# FastAPI REST API Documentation

The Bank Statement Table Extraction backend is implemented in **FastAPI**, providing endpoints for statement table parsing, transaction categorization, layout profiling, and health monitoring.

---

## Interactive API Documentation

When the FastAPI server is running:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Endpoints

### 1. `GET /health`
Returns system status, active version, loaded machine learning components, and supported profiles.

**Response `200 OK`**:
```json
{
  "status": "healthy",
  "service": "Bank Statement Table Extraction API",
  "version": "1.0.0",
  "brd_series": "Bank Muscat Series",
  "ml_line_classifier_loaded": true,
  "nlp_categorizer_loaded": true,
  "supported_profiles": [
    "bank_muscat",
    "straits_capital",
    "liberty_national",
    "continental_trust",
    "silk_road",
    "harbour_bank",
    "generic"
  ],
  "timestamp": 1729965000.123
}
```

---

### 2. `GET /profiles`
Returns metadata and formatting specifications for all supported bank profiles.

**Response `200 OK`**:
```json
{
  "profiles": [
    {
      "id": "bank_muscat",
      "name": "Bank Muscat",
      "country": "OM",
      "currency": "OMR",
      "currency_decimals": 3,
      "date_format": "DD/MM/YYYY",
      "direction_derivation": "separate-columns",
      "multi_account": false
    },
    {
      "id": "straits_capital",
      "name": "Straits Capital",
      "country": "SG",
      "currency": "SGD",
      "currency_decimals": 2,
      "date_format": "DD/MM/YYYY",
      "direction_derivation": "separate-columns",
      "multi_account": false
    }
  ],
  "count": 7
}
```

---

### 3. `POST /extract`
Extracts, normalizes, validates, and categorizes transaction tables from an uploaded statement PDF.

**Parameters (multipart/form-data)**:
- `file`: PDF statement file (binary, max 20 MB).
- `profile`: Profile ID (`auto`, `bank_muscat`, `straits_capital`, etc. Default: `auto`).
- `output_format`: `json`, `csv`, or `benchmark` (Default: `json`).
- `use_ml`: Boolean flag to enable scikit-learn layout classification (Default: `true`).
- `use_transformers`: Boolean flag to enable Hugging Face Transformers for NLP (Default: `false`).

#### Example cURL Command:
```bash
curl -X POST "http://localhost:8000/extract" \
  -F "file=@data/raw/bank_muscat_sample.pdf" \
  -F "profile=bank_muscat" \
  -F "output_format=json" \
  -F "use_ml=true"
```

#### Example Response `200 OK` (JSON):
```json
{
  "metadata": {
    "content_hash": "a4d3e589...",
    "file_name": "bank_muscat_sample.pdf",
    "page_count": 1,
    "bank": "Bank Muscat",
    "profile_used": "bank_muscat",
    "currency": "OMR",
    "transaction_count": 7,
    "extraction_method": "ml_enhanced",
    "processing_time_seconds": 0.0571
  },
  "accounts": [
    {
      "id": "acc-031501234567001",
      "account_number": "0315-01234567-001",
      "name": "Account 0315-01234567-001",
      "iban": null,
      "currency": "OMR",
      "opening_balance": null,
      "closing_balance": null
    }
  ],
  "transactions": [
    {
      "date": "2025-01-02",
      "value_date": "2025-01-02",
      "description": "SALARY CREDIT PETROLEUM DEV OMAN EMPLOYEE ID PDO-99120",
      "amount": 850.500,
      "direction": "credit",
      "balance": 2350.500,
      "currency": "OMR",
      "category": "INCOME_SALARY",
      "channel": "SALARY_CREDIT",
      "reference_id": "FT2500291823",
      "account_id": "acc-031501234567001",
      "original_data": {
        "Date": "02/01/2025",
        "Value Date": "02/01/2025",
        "Description / Narration": "SALARY CREDIT PETROLEUM DEV OMAN\nEMPLOYEE ID PDO-99120",
        "Ref / Chq No": "FT2500291823",
        "Debit (OMR)": "",
        "Credit (OMR)": "850.500",
        "Balance (OMR)": "2,350.500"
      }
    }
  ],
  "validation": {
    "reconciled": true,
    "opening_balance": 1500.000,
    "closing_balance": 2199.500,
    "calculated_closing_balance": 2199.500,
    "total_debits": 221.500,
    "total_credits": 921.000,
    "net_change": 699.500,
    "discrepancy_count": 0,
    "discrepancies": [],
    "warnings": []
  }
}
```

---

### 4. `POST /categorize`
Performs NLP classification and entity extraction on arbitrary transaction descriptions.

**Request Payload**:
```json
{
  "descriptions": [
    "SALARY CREDIT PETROLEUM DEVELOPMENT OMAN",
    "ATM CASH WITHDRAWAL MUSCAT GRAND MALL",
    "POS PURCHASE LULU HYPERMARKET"
  ],
  "use_transformers": false
}
```

**Response `200 OK`**:
```json
{
  "results": [
    {
      "description": "SALARY CREDIT PETROLEUM DEVELOPMENT OMAN",
      "category": "INCOME_SALARY",
      "confidence": 0.9412,
      "channel": "SALARY_CREDIT",
      "reference_id": null,
      "counterparty": null
    },
    {
      "description": "ATM CASH WITHDRAWAL MUSCAT GRAND MALL",
      "category": "ATM_CASH",
      "confidence": 0.8875,
      "channel": "ATM",
      "reference_id": null,
      "counterparty": null
    },
    {
      "description": "POS PURCHASE LULU HYPERMARKET",
      "category": "MERCHANT_POS",
      "confidence": 0.9120,
      "channel": "POS",
      "reference_id": null,
      "counterparty": null
    }
  ],
  "model_used": "scikit-learn TF-IDF Classifier"
}
```
