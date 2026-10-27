# Bank Statement Table Extraction & Banking Analytics
### Bank Muscat BRD Series — Implementation Deliverable

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141.1-green.svg)](https://fastapi.tiangolo.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.8.0-orange.svg)](https://scikit-learn.org/)
[![Transformers](https://img.shields.io/badge/Hugging%20Face-Transformers-yellow.svg)](https://huggingface.co/)
[![Tests](https://img.shields.io/badge/tests-41%20passed-brightgreen.svg)](https://docs.pytest.org/)

Production-ready Bank Statement Table Extraction pipeline and FastAPI backend developed for the **Bank Muscat Business Requirements Document (BRD) Series**. The system reliably extracts, normalizes, validates, and categorizes tabular transaction data from PDF bank statements across international banking formats and Bank Muscat (OMR 3-decimal currency).

---

## 1. Prescribed Technology Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Programming Language** | Python 3.11+ | Core implementation language |
| **Backend & REST API** | FastAPI | Asynchronous REST API serving `/extract`, `/categorize`, `/profiles`, `/health` |
| **Machine Learning** | scikit-learn | Layout line role classifier (`RandomForestClassifier`) & fast text categorizer |
| **NLP & Deep Learning** | Hugging Face Transformers | Natural Language Inference (NLI) zero-shot classification (`typeform/distilbert-base-uncased-mnli`) |
| **Document Processing** | PyMuPDF (fitz) | High-speed PDF vector token extraction and coordinate geometry |
| **Data Validation** | Pydantic v2 | Validated request/response schemas and accounting checks |
| **Test Suite** | pytest | 41 automated functional, unit, security, and integration tests |

---

## 2. Project Architecture & Structure

```
mayank/
├── app/
│   ├── main.py                  # FastAPI application entrypoint
│   ├── api/
│   │   └── endpoints.py         # REST endpoints (/extract, /categorize, /profiles, /health)
│   ├── extraction/
│   │   ├── assembler.py         # Transaction row assembly and cell extraction
│   │   ├── coordinate_extractor.py # PyMuPDF coordinate and token stream parser
│   │   ├── profiles.py          # Bank layout profiles (Bank Muscat, Straits Capital, etc.)
│   │   └── table_detector.py    # Column anchor detection and x-interval partitioning
│   ├── models/
│   │   ├── line_classifier.py   # Scikit-learn line role classifier (RandomForest)
│   │   └── nlp_categorizer.py   # Scikit-learn + Hugging Face transaction categorizer
│   ├── schemas/
│   │   └── transaction.py       # Pydantic schemas (Transaction, Account, Validation)
│   ├── services/
│   │   └── extractor.py         # End-to-end extraction orchestrator service
│   └── validation/
│       ├── balance_checker.py   # Running balance and closing balance accounting checks
│       └── normalizer.py        # ISO-8601 date parsing and multi-locale amount normalization
├── data/
│   ├── bankstatemently_benchmark/ # Dataset A: 5 released benchmark statements
│   ├── raw/                     # Raw input PDFs (including bank_muscat_sample.pdf)
│   ├── processed/               # Extracted CSV/JSON outputs
│   └── evaluation/              # Quantitative benchmark evaluation results
├── docs/
│   ├── API_DOCUMENTATION.md     # Detailed API endpoint documentation and cURL examples
│   ├── DATASET_SELECTION_AND_LICENSING.md # Audit and selection notes for Datasets A, B, C, D
│   ├── MODEL_DOCUMENTATION.md   # ML/NLP architecture, features, and baseline comparisons
│   └── TECHNICAL_REPORT.md      # Comprehensive engineering and BRD compliance report
├── scripts/
│   ├── acquire_datasets.py      # Dataset audit and acquisition script
│   ├── evaluate_benchmark.py    # Quantitative benchmark evaluation comparing baseline vs ML
│   └── generate_bank_muscat_sample.py # ReportLab generator for synthetic Bank Muscat PDF
├── tests/
│   ├── test_api.py              # FastAPI endpoint tests
│   ├── test_balance_checker.py  # Accounting reconciliation and discrepancy tests
│   ├── test_extraction_pipeline.py # End-to-end pipeline tests on all statements
│   ├── test_models.py           # ML LineClassifier and NLPCategorizer unit tests
│   └── test_normalizer.py       # Date parsing and amount normalization unit tests
├── .env.example                 # Environment configuration template
├── .gitignore                   # Git ignore file
├── requirements.txt             # Pinned project dependencies
└── README.md                    # Project documentation
```

---

## 3. Installation & Setup

### Prerequisites
- Python 3.11+
- Git

### Step 1: Clone or Navigate to Project
```bash
cd c:\Users\ASUS\Downloads\mayank
```

### Step 2: Create and Activate Virtual Environment (Recommended)
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
cp .env.example .env
```

---

## 4. Running the Application

### Start FastAPI Backend Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Once started, access:
- **API Health**: [http://localhost:8000/health](http://localhost:8000/health)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 5. Execution Commands

### Run Automated Test Suite
```bash
pytest -v
```
*(Executes 41 automated unit and integration tests covering API endpoints, normalization, ML models, regression checks, security headers/magic bytes, and statement extraction).*

### Run Quantitative Benchmark Evaluation
```bash
python scripts/evaluate_benchmark.py
```
*(Evaluates Baseline vs ML-Enhanced parser across all 5 benchmark statements and the Bank Muscat sample statement, printing precision, recall, and balance reconciliation metrics).*

### Run Independent NLP Model Benchmark (scikit-learn vs Transformers)
```bash
python scripts/evaluate_nlp_models.py
```
*(Evaluates scikit-learn vs Hugging Face Transformers across 80 independent banking narratives, computing accuracy, Macro-F1, confusion matrices, and latency).*

### Run Transformer & Model Verification
```bash
python scripts/verify_transformer.py
```
*(Audits Transformer architecture compatibility, transparent error handling without silent fallbacks, and verifies the scikit-learn classifier).*

### Run End-to-End Runtime Transformer Inference Smoke Test
```bash
python scripts/verify_runtime_inference.py
```
*(Executes actual Transformer inference across 7 banking narratives, tests the FastAPI /categorize endpoint with use_transformers=true, and verifies HTTP 503 error handling).*

### Generate Bank Muscat Sample Statement
```bash
python scripts/generate_bank_muscat_sample.py
```
*(Generates `data/raw/bank_muscat_sample.pdf` matching Bank Muscat 3-decimal OMR format).*

---

## 6. Sample API Request & Response

### Extract Statement via cURL
```bash
curl -X POST "http://localhost:8000/extract" \
  -F "file=@data/raw/bank_muscat_sample.pdf" \
  -F "profile=bank_muscat" \
  -F "output_format=json" \
  -F "use_ml=true"
```

### Sample Output (Truncated JSON):
```json
{
  "metadata": {
    "content_hash": "a4d3e5892b1f8c...",
    "file_name": "bank_muscat_sample.pdf",
    "page_count": 1,
    "bank": "Bank Muscat",
    "profile_used": "bank_muscat",
    "currency": "OMR",
    "transaction_count": 7,
    "extraction_method": "ml_enhanced",
    "processing_time_seconds": 0.0571
  },
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
      "reference_id": "FT2500291823"
    }
  ],
  "validation": {
    "reconciled": true,
    "total_debits": 221.500,
    "total_credits": 921.000,
    "discrepancy_count": 0,
    "warnings": []
  }
}
```

---

## 7. Quantitative Benchmark Results Summary

Evaluated against the **Bankstatemently Open Benchmark** (development set) and the **Bank Muscat Sample** (synthetic validation) using rigorous 1-to-1 transaction matching:

### Detailed Performance Breakdown (ML-Enhanced Pipeline)
| Statement ID | Institution / Country | Expected | Extracted | TP | FP | FN | Precision | Recall | F1-Score | Exact Match Acc | Balance Check | ML Latency |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **bsb-001** | Straits Capital (SG) | 12 | 12 | 12 | 0 | 0 | 100.0% | 100.0% | 100.0% | 100.0% (12/12) | PASS | 152.8 ms |
| **bsb-002** | Liberty National (US) | 15 | 15 | 15 | 0 | 0 | 100.0% | 100.0% | 100.0% | 100.0% (15/15) | PASS | 239.1 ms |
| **bsb-003** | Continental Trust (NL) | 22 | 22 | 22 | 0 | 0 | 100.0% | 100.0% | 100.0% | 100.0% (22/22) | PASS | 138.9 ms |
| **bsb-004** | Silk Road Banking (HK) | 25 | 25 | 25 | 0 | 0 | 100.0% | 100.0% | 100.0% | 100.0% (25/25) | PASS | 305.8 ms |
| **bsb-005** | Harbour Bank (CA) | 25 | 25 | 25 | 0 | 0 | 100.0% | 100.0% | 100.0% | 100.0% (25/25) | PASS | 90.7 ms |
| **bank_muscat** | Bank Muscat (OM - Synthetic) | 7 | 7 | 7 | 0 | 0 | 100.0% | 100.0% | 100.0% | 100.0% (7/7) | PASS | 53.8 ms |
| **TOTAL** | **All 6 Statements** | **106** | **106** | **106** | **0** | **0** | **100.00%** | **100.00%** | **100.00%** | **100.00% (106/106)** | **100% (6/6)** | **163.5 ms** |

### Field-Level Accuracy Breakdown (Reconciled Aggregate)
| Statement ID | Institution / Country | Date Accuracy | Description Accuracy | Debit Amount Accuracy | Credit Amount Accuracy | Balance Accuracy |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **bsb-001** | Straits Capital (SG) | 12 / 12 (100.0%) | 12 / 12 (100.0%) | 9 / 9 (100.0%) | 3 / 3 (100.0%) | 12 / 12 (100.0%) |
| **bsb-002** | Liberty National (US) | 15 / 15 (100.0%) | 15 / 15 (100.0%) | 14 / 14 (100.0%) | 1 / 1 (100.0%) | N/A (Credit Card) |
| **bsb-003** | Continental Trust (NL) | 22 / 22 (100.0%) | 22 / 22 (100.0%) | 17 / 17 (100.0%) | 5 / 5 (100.0%) | N/A (No Line Bal) |
| **bsb-004** | Silk Road Banking (HK) | 25 / 25 (100.0%) | 25 / 25 (100.0%) | 19 / 19 (100.0%) | 6 / 6 (100.0%) | 25 / 25 (100.0%) |
| **bsb-005** | Harbour Bank (CA) | 25 / 25 (100.0%) | 25 / 25 (100.0%) | 18 / 18 (100.0%) | 7 / 7 (100.0%) | 25 / 25 (100.0%) |
| **bank_muscat** | Bank Muscat (OM - Synthetic) | 7 / 7 (100.0%) | 7 / 7 (100.0%) | 5 / 5 (100.0%) | 2 / 2 (100.0%) | 7 / 7 (100.0%) |
| **TOTAL** | **All 106 Transactions** | **106 / 106 (100.0%)** | **106 / 106 (100.0%)** | **82 / 82 (100.0%)** | **24 / 24 (100.0%)** | **69 / 69 (100.0%)** |

*Baseline Comparison*: Pure rule-based heuristics achieved 103/106 extracted (TP=103, FP=0, FN=3, Precision=100.00%, Recall=97.17%, F1=98.56%, Exact Match=96.23%, Reconciled=83.3%), dropping transactions in `bsb-003` (overlay disclaimer) and `bsb-005` (page-split continuation). The scikit-learn `LineClassifier` eliminated both failure modes.

---

## 8. Bank Muscat Compliance, Model & Licensing Notes

- **Bank Muscat Requirements**: Accommodates 3-decimal currencies (`OMR`), bilingual English/Arabic headers (`بنك مسقط`), reference codes (`FT...`, `ATM...`, `POS...`, `OT...`, `CHG...`), and running balance reconciliation checks.
- **Hugging Face Transformer & ML Operational Architecture**:
  - `distilbert-base-uncased` is a Masked Language Model, not an NLI model. Zero-shot classification requires a fine-tuned Natural Language Inference model (`typeform/distilbert-base-uncased-mnli`, 255 MB).
  - Silent fallbacks have been eliminated: if transformer weights are not cached locally, an explicit `RuntimeError` and HTTP 503 is returned rather than falsely claiming Transformer inference.
  - Zero-shot candidate hypotheses are formatted with descriptive banking semantics (`retail store shopping or merchant purchase`, `bank fee or account maintenance charge`), eliminating previous misclassifications on POS purchases and service fees.
  - Held-out 80-example synthetic benchmark evaluation (`data/evaluation/nlp_benchmark_results.json`): `scikit-learn` achieves **83.75% accuracy (84.76% Macro-F1) in 0.32 ms**, while zero-shot Transformers achieve **41.25% accuracy (37.33% Macro-F1) in 104.09 ms**, an accuracy difference of **42.50 percentage points**. Evaluated as a held-out synthetic benchmark, not evidence of enterprise-level generalization. The lightweight scikit-learn model remains the default production path ($325\times$ faster, 0 external downloads).
- **Evaluation Scope Disclosure**:
  - `bsb-001` through `bsb-005`: Evaluated as a development set / benchmark sample suite.
  - `bank_muscat`: Evaluated on synthetic-sample validation (`data/raw/bank_muscat_sample.pdf`). Proprietary customer statements were unavailable; production deployment requires authorization and validation on real Bank Muscat customer statements.
  - `Scanned PDFs`: The system inspects for digital vector text layers. Image-only scanned PDFs are identified and returned with an informative warning (HTTP 200); no OCR extraction is performed without an upstream OCR engine.
- **Dataset Licensing**:
  - `Dataset A (Bankstatemently)`: MIT License — 5 released statements utilized; 10 pending.
  - `Dataset B & C (Panhapich)`: MIT License — Audited and rejected (3.5 GB YOLO image models unnecessary for digital PDF vector parsing).
  - `Dataset D (SynFinTabs)`: Academic Open Access — Audited and rejected (7.64 GB download focused on corporate balance sheets, not transaction ledgers).
- **Security & Privacy**: Zero third-party LLM cloud API dependencies; 100% local CPU execution. Verbatim `originalData` preserved for tamper-proof audit trails.

---

## 9. Containerization, Docker & Cloud Deployment

### Docker Build & Run
The application includes a production-grade multi-stage `Dockerfile`:
```bash
# Build production Docker container
docker build -t bank-statement-extractor:latest .

# Run container (exposing port 8000)
docker run -p 8000:8000 --env-file .env bank-statement-extractor:latest
```

### Live Cloud Deployment (Vercel Serverless)
The service is deployed live on Vercel as a serverless ASGI application:
- **Production URL**: `https://mayank-ten-indol.vercel.app`
- **Health Check**: `https://mayank-ten-indol.vercel.app/health`
- **Supported Profiles**: `https://mayank-ten-indol.vercel.app/profiles`
- **Architecture**: Vercel Python 3.12 Serverless Function via `api/index.py` and `vercel.json` rewrites. Read-only filesystem hardened, optimized lightweight ML stack (< 1 MB bundle, sub-second execution).

To run live cloud verification against the Vercel deployment:
```bash
python scripts/test_vercel_live.py
```
*(Validates all 7 live cloud endpoints: GET /, GET /health, GET /profiles, POST /categorize, POST /extract JSON, POST /extract CSV, and 400 security rejection).*

### Cloud Deployment (Render / PaaS)
A turnkey `render.yaml` blueprint is provided:
1. Connect repository to Render (or compatible cloud container provider).
2. Set build command: `pip install -r requirements.txt` (or Docker build).
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
4. Configure `/health` as the health check endpoint.
5. Set `API_KEY` in environment variables if authentication is required.

### Live Network Verification
Run the automated end-to-end socket verification script:
```bash
python scripts/verify_live_api.py
```
*(Binds to a live local TCP socket, launches the API server in a background thread, and validates 7/7 HTTP endpoints and security mechanisms).*
