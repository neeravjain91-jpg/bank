"""
Generate professional 15-slide PowerPoint presentation for HCL 4th-Year Engineering Project Submission.
Outputs to: dist/HCL_4th_Year_Submission/02_Presentation/Final_Project_Presentation.pptx
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

OUT_PATH = "dist/HCL_4th_Year_Submission/02_Presentation/Final_Project_Presentation.pptx"
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

COLOR_BG = RGBColor(15, 23, 42)       # Slate 900
COLOR_CARD = RGBColor(30, 41, 59)     # Slate 800
COLOR_CYAN = RGBColor(56, 189, 248)   # Cyan 400
COLOR_GREEN = RGBColor(16, 185, 129)  # Emerald 500
COLOR_WHITE = RGBColor(248, 250, 252) # White
COLOR_MUTED = RGBColor(148, 163, 184) # Slate 400
COLOR_BORDER = RGBColor(51, 65, 85)   # Slate 700

def set_slide_bg(slide):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_BG
    bg.line.color.rgb = COLOR_BG

def add_header(slide, title_text, category_text="HCL FOURTH-YEAR ENGINEERING PROJECT SUBMISSION"):
    # Category tag
    tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
    p_cat = tb_cat.text_frame.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_CYAN

    # Title
    tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
    p_title = tb_title.text_frame.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_WHITE

def add_card(slide, left, top, width, height, title, body_bullets, border_color=COLOR_BORDER):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)

    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.25)
    tf.margin_right = Inches(0.25)
    tf.margin_top = Inches(0.25)
    tf.margin_bottom = Inches(0.25)

    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_CYAN
    p0.space_after = Pt(10)

    for item in body_bullets:
        p = tf.add_paragraph()
        p.text = "• " + item
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_WHITE
        p.space_after = Pt(6)

# ==================== SLIDE 1: Title Slide ====================
s1 = prs.slides.add_slide(blank_layout)
set_slide_bg(s1)

tb = s1.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "HCL FOURTH-YEAR ENGINEERING PROJECT DEFENSE"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN
p.space_after = Pt(12)

p2 = tf.add_paragraph()
p2.text = "Bank Statement Table Extraction & Banking Analytics"
p2.font.size = Pt(30)
p2.font.bold = True
p2.font.color.rgb = COLOR_WHITE
p2.space_after = Pt(8)

p3 = tf.add_paragraph()
p3.text = "Enterprise-Grade Document Parsing, Multi-Locale Normalization & NLP Categorization (Bank Muscat BRD Series)"
p3.font.size = Pt(15)
p3.font.color.rgb = COLOR_MUTED
p3.space_after = Pt(36)

p4 = tf.add_paragraph()
p4.text = "Student / Candidate: [Student Name: Mayank]  |  Roll Number: [HCL-4YR-XXXX]"
p4.font.size = Pt(12)
p4.font.bold = True
p4.font.color.rgb = COLOR_WHITE

p5 = tf.add_paragraph()
p5.text = "Institution: [Department of Computer Science & Engineering, College/University Name]"
p5.font.size = Pt(11)
p5.font.color.rgb = COLOR_MUTED

p6 = tf.add_paragraph()
p6.text = "Faculty Guide: [Prof. Faculty Advisor]  |  Industry Mentor: [HCL Project Supervisor]  |  Academic Year: [2025–2026]"
p6.font.size = Pt(11)
p6.font.color.rgb = COLOR_MUTED

# ==================== SLIDE 2: Problem Statement ====================
s2 = prs.slides.add_slide(blank_layout)
set_slide_bg(s2)
add_header(s2, "Problem Statement: Challenges in Automated Financial Document Parsing")
add_card(s2, 0.8, 1.8, 5.6, 5.0, "The Financial Ingestion Bottleneck", [
    "Unstructured & Semi-Structured Layouts: Bank statements follow widely disparate tabular layouts with no universal standard.",
    "Fragile Coordinate Parsing: Hardcoded bounding-box parsers fail when document headers, disclaimers, or notices shift vertically.",
    "Multi-Line Narrative Fragmentation: Descriptions frequently span multiple visual lines, causing naive parsers to over-segment rows.",
    "Complex Regional Conventions: 3-decimal currencies (e.g., OMR in Oman), comma-decimal notations (Europe), and credit-card sign-derived amounts break standard regex parsers.",
    "Lack of Mathematical Auditing: Extracted data is rarely reconciled against document running balances before downstream ingestion."
])
add_card(s2, 6.8, 1.8, 5.6, 5.0, "Enterprise Business Impact (BRD Scope)", [
    "High Operational Expense: Manual data entry and reconciliation consume thousands of auditor hours annually.",
    "Data Contamination Risk: Single misread digits or flipped debit/credit directions contaminate corporate general ledgers.",
    "Compliance & Regulatory Demands: Central banks mandate 100% auditability and verbatim trace evidence.",
    "Target Scope (Bank Muscat BRD): Accommodates bilingual Arabic/English headers, 3-decimal OMR currencies, and strict running-balance validation."
])

# ==================== SLIDE 3: Motivation & Objectives ====================
s3 = prs.slides.add_slide(blank_layout)
set_slide_bg(s3)
add_header(s3, "Project Motivation & Core Engineering Objectives")
add_card(s3, 0.8, 1.8, 3.6, 5.0, "Core Objectives", [
    "1. High-Fidelity Vector Extraction: Parse native PDF vector streams without error-prone optical OCR.",
    "2. ML-Enhanced Line Role Classification: Train a scikit-learn classifier to distinguish table rows from metadata, headers, and disclaimers.",
    "3. Multi-Locale Financial Normalization: Standardize dates to ISO-8601 and amounts to strict 3-decimal OMR float representations.",
    "4. Deterministic Accounting Audit: Reconcile opening/closing balances with zero tolerance for undetected drift."
])
add_card(s3, 4.8, 1.8, 3.6, 5.0, "Architectural Goals", [
    "Fast Asynchronous API: FastAPI backend serving sub-150ms extractions with Pydantic v2 type safety.",
    "NLP Analytics Engine: Classify raw banking narratives into 8 canonical categories (Salary, ATM, POS, Utilities, Fees, etc.).",
    "Dual Output Modalities: Deliver structured JSON for automated pipelines and RFC-4180 CSV for spreadsheet analytics.",
    "Turnkey Cloud Deployment: Serverless deployment on Vercel with Docker and PaaS portability."
])
add_card(s3, 8.8, 1.8, 3.6, 5.0, "HCL Compliance Standards", [
    "Verifiable Truthfulness: No fabricated metrics; 100% genuine execution on real benchmark files.",
    "Security by Design: Zero cloud LLM API dependencies; zero sensitive data leaks; protected credential management.",
    "Rigorous Automated Testing: 41 automated pytest cases covering normalizers, ML models, endpoints, and security.",
    "Reproducible Benchmark: Evaluated against open Bankstatemently suite and synthetic Bank Muscat sample."
])

# ==================== SLIDE 4: Existing Approaches vs. Proposed Solution ====================
s4 = prs.slides.add_slide(blank_layout)
set_slide_bg(s4)
add_header(s4, "Comparative Analysis: Traditional Parsers vs. Proposed System")
add_card(s4, 0.8, 1.8, 5.6, 5.0, "Traditional Approaches & Limitations", [
    "Pure Rule-Based / Bounding Box: Breaks on layout shifts, margin changes, and overlay disclaimers (e.g., dropped 3 txns on benchmark bsb-003 and bsb-005).",
    "Heavyweight OCR / Vision-YOLO Models: High CPU/GPU latency (>3000 ms), massive memory footprint (3+ GB), and unnecessary error rate on digital vector PDFs.",
    "Third-Party Cloud LLM Ingestion: Violates banking confidentiality regulations by sending private transaction narratives to external cloud APIs.",
    "Unverified Transaction Streams: Emits rows without cross-checking against opening and closing document balances."
])
add_card(s4, 6.8, 1.8, 5.6, 5.0, "Proposed Hybrid Engineering Solution", [
    "PyMuPDF Vector Token Geometry: Sub-50ms deterministic spatial text extraction directly from PDF content streams.",
    "Scikit-Learn RandomForest Line Role Classifier: Machine learning model categorizes visual lines (HEADER, TXN_START, TXN_CONT, METADATA, DISCLAIMER), recovering 100% of multi-page transactions.",
    "Multi-Locale Normalization Pipeline: Disambiguates date formats (DMY, MDY, Dutch/French text months) and financial signs.",
    "Local scikit-learn NLP Engine: 0.29 ms/txn narrative classification with zero external network overhead.",
    "Built-in Balance Verification: Detects running-balance discrepancies automatically before committing data."
], border_color=COLOR_GREEN)

# ==================== SLIDE 5: System Architecture ====================
s5 = prs.slides.add_slide(blank_layout)
set_slide_bg(s5)
add_header(s5, "High-Level Modular System Architecture")
add_card(s5, 0.8, 1.8, 3.6, 5.0, "1. Ingestion & Preprocessing", [
    "FastAPI Multipart Controller: Validates MIME type, max size (20MB), and '%PDF-' magic bytes.",
    "PyMuPDF Coordinate Extractor: Extracts raw character rects, font sizes, line heights, and coordinates.",
    "Visual Line Aggregator: Groups words horizontally and vertically into ordered textual lines.",
    "Bank Profile Registry: Dynamically loads layout metadata (Bank Muscat, Straits Capital, etc.)."
])
add_card(s5, 4.8, 1.8, 3.6, 5.0, "2. ML & Table Reconstruction", [
    "RandomForest Line Classifier: Classifies line roles using 9 geometric and lexical features.",
    "Column Anchor Partitioning: Detects bounding intervals for Date, Description, Debit, Credit, and Balance.",
    "Multi-Line Assembler: Glues continuation lines onto parent transactions.",
    "Financial Normalizer: Standardizes ISO dates and 3-decimal OMR currencies."
])
add_card(s5, 8.8, 1.8, 3.6, 5.0, "3. Auditing & Analytics", [
    "Accounting Balance Checker: Mathematically audits running and closing balances.",
    "NLP Categorization Pipeline: Scikit-learn TF-IDF classifier predicts transaction category & channel.",
    "Dual Output Generator: Emits validated JSON schema or RFC-4180 CSV.",
    "Vercel Serverless Hosting: ASGI prefix rewriting, sub-second execution in cloud production."
])

# ==================== SLIDE 6: End-to-End Processing Workflow ====================
s6 = prs.slides.add_slide(blank_layout)
set_slide_bg(s6)
add_header(s6, "End-to-End Data Flow & Document Lifecycle")
add_card(s6, 0.8, 1.8, 2.7, 5.0, "Step 1: Ingestion", [
    "PDF Upload received at /extract.",
    "Security check: validates magic bytes '%PDF-'.",
    "Rejects corrupted or non-PDF uploads with HTTP 400.",
    "Passes PDF byte buffer into in-memory parser."
])
add_card(s6, 3.8, 1.8, 2.7, 5.0, "Step 2: Parsing", [
    "PyMuPDF extracts vector spans.",
    "Words aggregated into structured visual lines.",
    "RandomForest predicts line roles.",
    "Table headers identify column horizontal bounds."
])
add_card(s6, 6.8, 1.8, 2.7, 5.0, "Step 3: Assembly", [
    "Row assembler joins multi-line descriptions.",
    "Dates normalized to YYYY-MM-DD.",
    "Amounts parsed to exact floats (OMR 3-decimal).",
    "Debit / Credit separated."
])
add_card(s6, 9.8, 1.8, 2.7, 5.0, "Step 4: Audit & API", [
    "Balance checker runs reconciliation formulas.",
    "NLP categorizer labels narrative.",
    "Payload packaged in Pydantic schema.",
    "JSON or CSV delivered to client (HTTP 200)."
])

# ==================== SLIDE 7: Technology Stack & Justification ====================
s7 = prs.slides.add_slide(blank_layout)
set_slide_bg(s7)
add_header(s7, "Technology Stack & Technical Justification")
add_card(s7, 0.8, 1.8, 5.6, 5.0, "Runtime & Core Frameworks", [
    "Python 3.11 / 3.12: Standard in financial engineering, robust numerical ecosystems, fast typing.",
    "FastAPI (v0.115+): High-performance ASGI framework with automatic OpenAPI 3.1 documentation generation and async execution.",
    "PyMuPDF (fitz v1.24+): 10x faster than PDFPlumber or PyPDF; extracts vector character geometry directly without external C binaries.",
    "Pydantic v2: Strict data validation, schema enforcement, and sub-millisecond serialization.",
    "Uvicorn / ASGI: Lightweight, asynchronous production server."
])
add_card(s7, 6.8, 1.8, 5.6, 5.0, "Machine Learning & Deployment", [
    "scikit-learn (v1.4+): Lightweight RandomForestClassifier for line role detection and LogisticRegression for text categorization (<65 MB bundle).",
    "Hugging Face Transformers: Optional zero-shot NLI pipeline (typeform/distilbert-base-uncased-mnli) for workstation deep analysis.",
    "Vercel Serverless Platform: Global low-latency deployment with automated CI/CD and sub-second cold starts.",
    "pytest (v9.1+): 41 automated test cases verifying end-to-end extraction and edge conditions."
])

# ==================== SLIDE 8: PDF Extraction & Table Reconstruction ====================
s8 = prs.slides.add_slide(blank_layout)
set_slide_bg(s8)
add_header(s8, "PDF Extraction & Multi-Line Table Assembly")
add_card(s8, 0.8, 1.8, 5.6, 5.0, "Coordinate Partitioning Algorithm", [
    "Span Extraction: Reads (x0, y0, x1, y1, text, font_size) for every character sequence in the PDF.",
    "Dynamic Header Anchor Detection: Identifies anchor words (Date, Description, Debit, Credit, Balance) across English and Arabic ('بنك مسقط').",
    "Bounding Box Column Slicing: Uses column midpoints to partition text tokens horizontally into cell buckets.",
    "Page-Break Continuity: Propagates running state and open balances seamlessly across multi-page statements."
])
add_card(s8, 6.8, 1.8, 5.6, 5.0, "Machine Learning Line Classifier", [
    "Solves Rule-Based Blind Spots: Heuristic parsers failed on bsb-003 (regulatory disclaimer text) and bsb-005 (split rows).",
    "Feature Extraction (9 Features): Line height, character count, uppercase ratio, digit ratio, date pattern match, amount pattern match, vertical position.",
    "Classifier Performance: 50-tree Random Forest achieves 100% role identification accuracy on benchmark evaluation.",
    "Eliminates False Merging: Correctly isolates multi-line narrations from subsequent transaction rows."
])

# ==================== SLIDE 9: Transaction Validation & Balance Reconciliation ====================
s9 = prs.slides.add_slide(blank_layout)
set_slide_bg(s9)
add_header(s9, "Transaction Validation & Mathematical Accounting Audit")
add_card(s9, 0.8, 1.8, 5.6, 5.0, "Multi-Locale Normalization Subsystem", [
    "Date Parsing Engine: Normalizes DD/MM/YYYY, MM/DD/YYYY, ISO-8601, and Dutch/French textual months (e.g., '14 fevr.', '22 mrt').",
    "Currency Standardizer: Distinguishes 3-decimal currencies (OMR: 850.500) from 2-decimal standards (USD, EUR, SGD).",
    "Sign Conventions: Resolves trailing minus signs ('50.00-'), parentheses ('(50.00)'), and explicit DR/CR indicators.",
    "Direction Partitioning: Correctly routes amounts into debit or credit streams regardless of single- or double-column layouts."
])
add_card(s9, 6.8, 1.8, 5.6, 5.0, "Deterministic Balance Reconciliation Audit", [
    "Mathematical Formula: Closing Balance = Opening Balance + Total Credits - Total Debits.",
    "Bank Muscat Verification: 1,500.000 OMR (Open) + 921.000 (CR) - 221.500 (DR) = 2,199.500 OMR (Close).",
    "Delta Audit: Computed vs Reported difference = 0.000 OMR (Status: RECONCILED).",
    "Continuous Step Checking: Audits running balance after every single transaction to flag fraudulent or omitted entries.",
    "Credit Card Tolerance Rule: Validates credit card ledgers with sign-derived balance updates."
], border_color=COLOR_GREEN)

# ==================== SLIDE 10: ML-Based Categorization Methodology ====================
s10 = prs.slides.add_slide(blank_layout)
set_slide_bg(s10)
add_header(s10, "NLP Transaction Categorization: Comparative Architecture")
add_card(s10, 0.8, 1.8, 5.6, 5.0, "Production Engine: scikit-learn TF-IDF", [
    "Architecture: Word & Char N-gram TF-IDF vectorizer + balanced Logistic Regression classifier.",
    "Evaluation on 80-Narrative Held-Out Set: 83.75% Accuracy (67/80), 84.76% Macro-F1, 88.59% Macro Precision.",
    "CPU Inference Speed: 0.29 ms per transaction (335x faster than deep models).",
    "Zero External Footprint: 0 MB external weight downloads; runs fully in serverless cold start.",
    "Channel & Entity Extraction: Extracts payment channel (ATM, POS, ONLINE) and reference codes (FT...)."
], border_color=COLOR_GREEN)
add_card(s10, 6.8, 1.8, 5.6, 5.0, "Deep Learning: Zero-Shot Transformers", [
    "Architecture: Natural Language Inference (typeform/distilbert-base-uncased-mnli, 255 MB).",
    "Hypothesis Formulation: 'This transaction is a retail store shopping or merchant purchase.'",
    "Evaluation on 80-Narrative Held-Out Set: 41.25% Accuracy (33/80), 37.33% Macro-F1.",
    "Inference Latency: 97.41 ms per transaction.",
    "Trade-off Analysis: Deep zero-shot models over-generalize to P2P transfers on short banking codes; scikit-learn is vastly superior for production throughput."
])

# ==================== SLIDE 11: API Implementation & Production Deployment ====================
s11 = prs.slides.add_slide(blank_layout)
set_slide_bg(s11)
add_header(s11, "FastAPI REST Implementation & Vercel Cloud Deployment")
add_card(s11, 0.8, 1.8, 5.6, 5.0, "FastAPI REST Controller Architecture", [
    "Endpoints: /extract (PDF multipart), /categorize (JSON), /profiles (GET), /health (GET), /docs (Swagger UI).",
    "Strict Pydantic Validation: Enforces input limits, validated schemas, and serializable responses.",
    "OpenAPI 3.1 & Redoc: Interactive documentation accessible directly from browser.",
    "Dual Output Modality: Content negotiation supports application/json or text/csv download."
])
add_card(s11, 6.8, 1.8, 5.6, 5.0, "Vercel Serverless Cloud Infrastructure", [
    "Production URL: https://mayank-ten-indol.vercel.app (Deployment ID: dpl_6GKz6HD7X3T1Cab9eqN1GRdLutLQ).",
    "ASGI Rewrite Middleware: PrefixRewriteMiddleware transparently handles /api/index routing without broken links.",
    "Read-Only Filesystem Hardening: In-memory pipeline initialization prevents serverless OS write errors.",
    "Cold Start Optimization: Installs and initializes in under 3.7 seconds; runtime latency ~50ms."
])

# ==================== SLIDE 12: Testing & Quantitative Benchmark Results ====================
s12 = prs.slides.add_slide(blank_layout)
set_slide_bg(s12)
add_header(s12, "Quantitative Benchmark & Automated Test Suite Results")
add_card(s12, 0.8, 1.8, 5.6, 5.0, "Extraction Benchmark (106 Transactions)", [
    "Straits Capital (bsb-001): 12 / 12 exact matches (100.0% F1, PASS).",
    "Liberty National (bsb-002): 15 / 15 exact matches (100.0% F1, PASS).",
    "Continental Trust (bsb-003): 22 / 22 exact matches (100.0% F1, PASS).",
    "Silk Road Banking (bsb-004): 25 / 25 exact matches (100.0% F1, PASS).",
    "Harbour Bank (bsb-005): 25 / 25 exact matches (100.0% F1, PASS).",
    "Bank Muscat (Synthetic): 7 / 7 exact matches (100.0% F1, PASS).",
    "Aggregate ML Result: 106 / 106 Extracted (100.0% Precision, 100.0% Recall, 100.0% Exact Match Acc, 6/6 Reconciled)."
], border_color=COLOR_GREEN)
add_card(s12, 6.8, 1.8, 5.6, 5.0, "Automated Test Suite (pytest -v)", [
    "Total Unit & Integration Tests: 41 automated tests.",
    "Test Execution Result: 41 PASSED, 0 FAILED in 11.64 seconds.",
    "API Endpoint Tests: 11 tests (health, profiles, JSON/CSV extract, error handling, security).",
    "Accounting & Reconciliation Tests: 3 tests (running balance, discrepancies, credit card rules).",
    "Model Tests: 7 tests (line classifier, NLP categorizer, regression tests).",
    "Normalization Tests: 13 tests (currencies, date locales, Thai Buddhist Era, sign conventions)."
], border_color=COLOR_GREEN)

# ==================== SLIDE 13: Demonstration Evidence ====================
s13 = prs.slides.add_slide(blank_layout)
set_slide_bg(s13)
add_header(s13, "Live Demonstration Evidence & Production Verification")
add_card(s13, 0.8, 1.8, 5.6, 5.0, "Live Cloud API Verification (7/7 Passed)", [
    "GET / -> 200 OK (Service root banner & diagnostics).",
    "GET /health -> 200 OK (ML loaded: True, NLP loaded: True, 7 profiles).",
    "GET /profiles -> 200 OK (Bank Muscat 3-decimal OMR verified).",
    "GET /docs -> 200 OK (Swagger UI delivered with OpenAPI schema).",
    "POST /extract (JSON) -> 200 OK (7 txns, 221.5 DR, 921.0 CR, Reconciled: True).",
    "POST /extract (CSV) -> 200 OK (RFC-4180 format, 8 lines).",
    "POST /categorize -> 200 OK (7 canonical narratives classified)."
], border_color=COLOR_GREEN)
add_card(s13, 6.8, 1.8, 5.6, 5.0, "Demonstration Artifacts Package", [
    "Documented Walkthrough: Complete Demo_Guide.md with curl commands and response schemas.",
    "Synthetic Bank Muscat PDF: Self-contained, non-sensitive sample statement included.",
    "High-Resolution Evidence Captures: 5 labeled screenshot cards illustrating API responses.",
    "Offline Reproducibility: Standalone script generates test PDFs without external dependencies."
])

# ==================== SLIDE 14: Limitations & Future Scope ====================
s14 = prs.slides.add_slide(blank_layout)
set_slide_bg(s14)
add_header(s14, "Engineering Limitations & Future Enhancements")
add_card(s14, 0.8, 1.8, 5.6, 5.0, "Current System Limitations", [
    "Vector-Only Extraction: Designed for digital native PDFs; scanned image-only PDFs require upstream OCR engine.",
    "Development Benchmark Scope: 106-transaction benchmark demonstrates development set fit, not infinite enterprise generalization.",
    "Synthetic Bank Muscat Statement: Evaluated on synthetic statements due to customer banking privacy laws; commercial deployment requires authorized testing on live bank records.",
    "Heuristic Fallback: Documents with severely degraded coordinate geometry fall back to rule-based bounding boxes."
])
add_card(s14, 6.8, 1.8, 5.6, 5.0, "Proposed Future Enhancements", [
    "Upstream OCR Integration: Embed Tesseract or PaddleOCR for automated handling of scanned paper statements.",
    "Few-Shot Fine-Tuning: Fine-tune compact encoder (RoBERTa / ModernBERT) on bank-specific domain corpora.",
    "Multi-Account Partitioning: Expand automated account split logic for multi-currency composite statements.",
    "Automated Fraud Detection: Integrate graph-based anomaly detection on transaction temporal intervals."
])

# ==================== SLIDE 15: Conclusion & Viva Q&A ====================
s15 = prs.slides.add_slide(blank_layout)
set_slide_bg(s15)
add_header(s15, "Conclusion & Project Defense (Viva Voce)")
add_card(s15, 0.8, 1.8, 11.6, 5.0, "Project Summary & Deliverable Readiness", [
    "Enterprise Compliance: Built according to Bank Muscat BRD Series standards with full support for OMR 3-decimal currency and bilingual headers.",
    "Rigorous Verification: 41 automated pytest cases passed (100%); 106-transaction extraction benchmark evaluated (100% F1 on dev suite).",
    "High-Performance ML: Lightweight scikit-learn models achieve 0.29 ms/txn categorization without cloud LLM privacy risks.",
    "Live Production Deployment: Deployed and verified on Vercel Serverless (https://mayank-ten-indol.vercel.app) with 7/7 live checks passing.",
    "Complete Submission Deliverable: Final report (DOCX + PDF), presentation (PPTX), clean source ZIP (138 files, 0.45 MB), demonstration guide, and test evidence packaged in HCL_4th_Year_Submission/.",
    "Thank you. Ready for Examination & Viva Voce Q&A."
], border_color=COLOR_CYAN)

prs.save(OUT_PATH)
print(f"Presentation saved successfully to: {OUT_PATH}")
