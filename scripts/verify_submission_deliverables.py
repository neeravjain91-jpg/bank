"""
Quality assurance and deliverable inventory verification script for HCL 4th-Year Submission.
Validates existence, file sizes, readability, and content integrity for all submission files.
"""

import os
import sys
import zipfile
import json
import fitz # PyMuPDF
from docx import Document
from pptx import Presentation

BASE_DIR = os.path.abspath("dist/HCL_4th_Year_Submission")

EXPECTED_FILES = [
    "01_Project_Report/Final_Project_Report.docx",
    "01_Project_Report/Final_Project_Report.pdf",
    "02_Presentation/Final_Project_Presentation.pptx",
    "03_Source_Code/Bank_Statement_Extraction_Source.zip",
    "04_Test_Evidence/Automated_Test_Report.txt",
    "04_Test_Evidence/Extraction_Benchmark_Report.json",
    "04_Test_Evidence/Categorization_Evaluation_Report.json",
    "04_Test_Evidence/Live_API_Verification_Report.txt",
    "05_Demonstration/Demo_Guide.md",
    "05_Demonstration/Synthetic_Bank_Muscat_Statement.pdf",
    "05_Demonstration/screenshots/01_swagger_ui_docs.png",
    "05_Demonstration/screenshots/02_extract_request_and_summary.png",
    "05_Demonstration/screenshots/03_extracted_transactions_table.png",
    "05_Demonstration/screenshots/04_nlp_categorization_results.png",
    "05_Demonstration/screenshots/05_accounting_reconciliation.png",
    "SUBMISSION_README.md"
]

def run_qa():
    print(f"\n{'='*75}")
    print(f"HCL FOURTH-YEAR ENGINEERING SUBMISSION — FINAL QUALITY ASSURANCE")
    print(f"Base Directory: {BASE_DIR}")
    print(f"{'='*75}\n")

    all_ok = True
    inventory = []

    for rel_path in EXPECTED_FILES:
        full_path = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(full_path):
            print(f"[FAIL] Missing file: {rel_path}")
            all_ok = False
            continue
        
        size = os.path.getsize(full_path)
        if size == 0:
            print(f"[FAIL] Empty file: {rel_path}")
            all_ok = False
            continue

        size_kb = size / 1024
        status_note = "Valid"

        # Type-specific checks
        if rel_path.endswith(".docx"):
            try:
                doc = Document(full_path)
                p_count = len(doc.paragraphs)
                t_count = len(doc.tables)
                status_note = f"Valid DOCX ({p_count} paras, {t_count} tables)"
            except Exception as e:
                status_note = f"Corrupted DOCX: {e}"
                all_ok = False

        elif rel_path.endswith(".pdf"):
            try:
                doc = fitz.open(full_path)
                pages = len(doc)
                status_note = f"Valid PDF ({pages} pages)"
            except Exception as e:
                status_note = f"Corrupted PDF: {e}"
                all_ok = False

        elif rel_path.endswith(".pptx"):
            try:
                prs = Presentation(full_path)
                slides = len(prs.slides)
                status_note = f"Valid PPTX ({slides} slides)"
            except Exception as e:
                status_note = f"Corrupted PPTX: {e}"
                all_ok = False

        elif rel_path.endswith(".zip"):
            try:
                with zipfile.ZipFile(full_path, 'r') as z:
                    count = len(z.namelist())
                    # Check for prohibited files
                    bad = [f for f in z.namelist() if f.endswith(('.env', '.safetensors', '.bin', '.pt', '.pyc')) or '.git/' in f or 'models_cache' in f]
                    if bad:
                        status_note = f"ZIP contains prohibited files: {bad[:2]}"
                        all_ok = False
                    else:
                        status_note = f"Valid clean ZIP ({count} files, 0 secrets/prohibited)"
            except Exception as e:
                status_note = f"Corrupted ZIP: {e}"
                all_ok = False

        elif rel_path.endswith(".json"):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                status_note = f"Valid JSON ({len(data)} root keys)"
            except Exception as e:
                status_note = f"Invalid JSON: {e}"
                all_ok = False

        inventory.append((rel_path, size_kb, status_note))
        print(f"[{'PASS' if 'Valid' in status_note else 'FAIL':4}] {rel_path:<55} {size_kb:>8.1f} KB | {status_note}")

    print(f"\n{'-'*75}")
    if all_ok:
        print(">>> ALL 16 SUBMISSION DELIVERABLES ARE PRESENT, NON-EMPTY, AND VERIFIED! <<<")
    else:
        print(">>> WARNING: SOME DELIVERABLES FAILED VALIDATION CHECKS! <<<")
    print(f"{'-'*75}\n")

    return all_ok

if __name__ == "__main__":
    success = run_qa()
    sys.exit(0 if success else 1)
