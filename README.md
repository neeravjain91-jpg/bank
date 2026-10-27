# Bank Statement Table Extraction & Banking Analytics

**Bank Muscat BRD Series — academic prototype**

This repository is the GitHub publication target for a Python/FastAPI bank-statement extraction project.

## Intended capabilities

- Extract transaction tables from digital-text PDF bank statements.
- Normalize transaction dates, amounts, debit/credit directions, and currencies.
- Validate running/closing balances where sufficient statement data is available.
- Return extracted transactions as JSON or CSV.
- Categorize transaction narratives with a lightweight scikit-learn model; optional Hugging Face zero-shot inference is experimental.
- Expose extraction and categorization through FastAPI.

## Technology stack

- Python 3.11
- FastAPI / Pydantic
- PyMuPDF
- scikit-learn
- Hugging Face Transformers (optional)
- pytest

## Current evaluation notes

Prior local audit reports describe 106 transactions across five public synthetic benchmark PDFs and one synthetic Bank Muscat sample. The reported extraction results are development/benchmark-sample results, not proof of generalization to unseen bank statement formats. The reported NLP benchmark contains 80 synthetic narratives; its evaluation results should be read with the documented tuning limitations.

The Bank Muscat sample is synthetic and does not establish accuracy on real customer statements. Image-only scanned PDFs are detected with a warning; OCR extraction is not implemented.

## Security and data

Use synthetic or properly authorized, redacted statements only. Do not commit API keys, secret environment files, model weights, customer statements, or private financial data. Configure API authentication before making upload endpoints publicly available.

## Status

This repository was initialized as the publication target. The full application source, tests, evaluation artifacts, and deployment configuration must be added from the verified local project before a working deployment can be claimed.
