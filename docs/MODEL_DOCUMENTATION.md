# Machine Learning & NLP Model Documentation
## Architecture, Training Methodology, Evaluation Rigor, and Limitations

---

## 1. Executive Summary

In strict accordance with the project directives, the application implements two distinct Machine Learning and NLP systems:
1. **Layout & Line Role Classifier**: Implemented in **`scikit-learn`** (`RandomForestClassifier` + `DictVectorizer`).
2. **Transaction Semantic Categorizer & Entity Extractor**: Implemented in **`scikit-learn`** (`TfidfVectorizer` + `LogisticRegression`) with optional zero-shot Natural Language Inference (NLI) classification via **`Hugging Face Transformers`** (`typeform/distilbert-base-uncased-mnli`).

Both components are genuinely integrated into the document extraction pipeline and execute locally on standard CPU hardware without external cloud API calls.

---

## 2. Line Role Classifier (`scikit-learn`)

### 2.1 Problem Formulation & Objective
Bank statement PDFs vary significantly in layout geometry, multi-line transaction continuation structures, legal footers, and metadata placement. The `LineClassifier` predicts the semantic role of visual text lines prior to transaction assembly:
- `TABLE_HEADER`: Column definitions (Date, Narration, Debit, Credit, Balance).
- `TRANSACTION_START`: First line of a transaction containing primary date and transaction data.
- `TRANSACTION_CONTINUATION`: Subsequent narrative lines belonging to the preceding transaction row.
- `METADATA_HEADER`: Account numbers, customer names, branch identifiers, statement periods.
- `BALANCE_SUMMARY`: Opening balance, closing balance, total debits, total credits.
- `NOISE_FOOTER`: Legal disclaimers, terms updates, pagination, regulatory notices.

### 2.2 Model Architecture & Feature Engineering
- **Pipeline**:
  1. `DictVectorizer`: One-hot encodes categorical features and scales numerical values.
  2. `RandomForestClassifier`: 50 estimators, max depth 8, random state 42.
- **Feature Vector**:
  - **Spatial Features**:
    - `rel_y0`: Normalized vertical coordinate ($y_0 / \text{page\_height}$).
    - `rel_x0`: Normalized horizontal coordinate ($x_0 / \text{page\_width}$).
    - `line_w`: Normalized width of line bounding box.
    - `line_h`: Vertical line height in points.
  - **Lexical & Orthographic Features**:
    - `digit_ratio`: Count of numeric digits divided by line length.
    - `upper_ratio`: Count of uppercase characters divided by line length.
    - `num_words`: Word token count.
  - **Regex Indicators**:
    - `starts_with_date`: Binary flag for lines starting with dates (`DD/MM`, `DD MMM`, `MM/DD`, etc.).
    - `has_date`, `has_amount`, `has_currency`: Regex matches for amounts and monetary symbols.
  - **Keyword Hits**: Multi-lingual dictionary matches for headers, balance summaries, and legal footers.
  - **Contextual Features**:
    - `prev_label`: Role assigned to the immediately preceding visual line.

### 2.3 Training Methodology & Development Set Disclosure
- **Training Set Composition**: Trained on 42 representative synthetic and exemplar layout patterns, augmented via coordinate perturbations ($\pm 5\text{ pt}$ vertical jitter).
- **Data Leakage & Evaluation Scope**:
  - The exemplar patterns in `train_default_model()` were derived from the geometric and lexical characteristics of the target benchmark statements (`bsb-001` through `bsb-005` and `bank_muscat`).
  - **Disclosure**: The benchmark statements were **not** isolated as an unseen holdout dataset. Consequently, performance metrics on this suite represent **development-set / benchmark-sample performance**.
  - While this demonstrates that the classifier resolves challenging failure modes (such as multi-line wrapping and footer contamination), it does not represent out-of-distribution generalization on uncalibrated, unseen banking layouts.

---

## 3. NLP Transaction Categorizer & Entity Extractor

### 3.1 Objective & Banking Taxonomy
Categorizes arbitrary transaction narrations into an 8-class banking analytics taxonomy and extracts semantic entities:
1. `INCOME_SALARY`: Payroll, employer deposits, wages.
2. `TRANSFER_P2P`: Person-to-person transfers, PayNow, FPS, SEPA transfers.
3. `MERCHANT_POS`: Retail, dining, grocery, e-commerce transactions.
4. `UTILITIES_SERVICES`: Electricity, water, telecommunications, municipal bills.
5. `ATM_CASH`: Cash withdrawals at automated teller machines.
6. `BANK_FEES`: Monthly maintenance fees, overdraft fees, account charges.
7. `INVESTMENT_DIVIDEND`: Stock dividends, mutual fund distributions.
8. `OTHER`: Unclassified or miscellaneous accounting adjustments.

### 3.2 Dual-Engine Implementation
- **Fast Production Mode (`scikit-learn`)**:
  - `TfidfVectorizer`: Sublinear term frequency, n-gram range (1, 2).
  - `LogisticRegression`: Multi-class logistic regression with balanced class weights (`class_weight='balanced'`) to prevent majority-class bias.
  - Latency: $<1\text{ ms}$ per transaction on CPU.
  - Verification: 100% accuracy on representative banking narrations (`scripts/verify_transformer.py`).
- **Deep Contextual Mode (`Hugging Face Transformers`)**:
  - **Audit Finding**: The base model `distilbert-base-uncased` has architecture `DistilBertForMaskedLM` and lacks an NLI classification head. Zero-shot classification requires a model fine-tuned on Natural Language Inference (MultiNLI) to map label hypotheses to entailment and contradiction.
  - **Compatible Architecture & Runtime Verification**: Configured and runtime-verified with `typeform/distilbert-base-uncased-mnli` (255.4 MB safetensors). Verified on CPU in `scripts/verify_runtime_inference.py`: loads in 7.23s, classifies banking narratives in 96.0 ms per transaction.
  - **Verified Cache Files**: Cached in `~/.cache/huggingface/hub/models--typeform--distilbert-base-uncased-mnli/snapshots/cfa538a0fddbbd978fefe8966c1aeff7ad409c90` (`config.json`, `model.safetensors`, `special_tokens_map.json`, `tokenizer_config.json`, `vocab.txt`).
  - **Zero Silent Fallback**: If model weights are not pre-cached locally or network is unavailable, the pipeline raises an explicit `RuntimeError` rather than silently catching the error and pretending Transformer inference occurred. The FastAPI endpoint returns HTTP 503 (`Service Unavailable`) explaining the cache requirement.
  - **Operational Recommendations**: For production deployments, pre-caching weights into `~/.cache/huggingface/hub` or using the fast scikit-learn classifier (<1 ms latency, 0 external dependencies) is recommended.

### 3.3 Entity Extraction Rules
- **Payment Channel**: Regex identification of `POS`, `ATM`, `PAYNOW`, `FPS`, `DIRECT_DEBIT`, `WIRE`, `CHEQUE`, `SALARY_CREDIT`, `ONLINE`.
- **Reference Identifier**: Extraction of transaction references (`FT...`, `REF: ...`, `POS-...`, `P...QR`).
- **Counterparty**: Extraction of recipient or merchant entity from `TO:`, `FROM:`, or IBAN patterns.

### 3.4 Zero-Shot Candidate Label Engineering & Ambiguity Thresholding
During runtime auditing, two systematic misclassifications were identified in the preliminary zero-shot Transformer configuration:
1. `POS PURCHASE LULU HYPERMARKET ...` was misclassified as `INVESTMENT_DIVIDEND` (score: 0.8559).
   - *Root Cause*: In MNLI pre-training corpora, the word "PURCHASE" frequently co-occurs with capital assets, securities, and corporate contracts. The unadorned candidate label `"Investment"` acted as a broad attractor.
2. `MONTHLY SERVICE FEE ACCOUNT MAINTENANCE ...` was misclassified as `UTILITIES_SERVICES` (score: 0.3750).
   - *Root Cause*: The phrase "MONTHLY SERVICE FEE" contains "monthly" and "service", which MNLI associated with recurring utility bill services, while `"Bank Fee"` lacked descriptive banking context.

**Resolution**:
- **Candidate Hypotheses**: Reformed into natural, mutually exclusive descriptive phrases:
  - `salary or wage payment` -> `INCOME_SALARY`
  - `funds transfer or payment to another person` -> `TRANSFER_P2P`
  - `retail store shopping or merchant purchase` -> `MERCHANT_POS`
  - `utility bill payment` -> `UTILITIES_SERVICES`
  - `ATM cash withdrawal` -> `ATM_CASH`
  - `bank fee or account maintenance charge` -> `BANK_FEES`
  - `investment dividend or securities distribution` -> `INVESTMENT_DIVIDEND`
- **Domain Hypothesis Template**: Configured as `"This bank transaction is a {}."` rather than the generic `"This example is {}."`.
- **Ambiguity & Confidence Thresholding**: Random chance across 7 candidate classes is $1/7 \approx 0.143$. If top confidence is $<0.22$ or the margin between the top two candidates is $<0.03$, the transaction is assigned to `OTHER` (uncertain/unclassified) rather than making a random guess.
- **Regression Outcomes**: On the runtime smoke test suite, both misclassifications were eliminated:
  - `POS PURCHASE LULU HYPERMARKET`: `MERCHANT_POS` (Confidence: 0.8902, PASS).
  - `MONTHLY SERVICE FEE ACCOUNT MAINTENANCE`: `BANK_FEES` (Confidence: 0.9883, PASS).

---

## 4. Quantitative Evaluation: Baseline vs. ML-Enhanced

### 4.1 Aggregate Benchmark Comparison
Evaluated across 106 reference transactions using identical ground-truth 1-to-1 matching rules:

| Metric | Rule-Based Baseline | ML-Enhanced Pipeline | Technical Impact |
| :--- | :---: | :---: | :--- |
| **Transaction True Positives (TP)** | 103 / 106 | **106 / 106** | All 106 transactions successfully extracted |
| **Transaction False Positives (FP)** | 0 | **0** | Zero false alarm transactions introduced |
| **Transaction False Negatives (FN)** | 3 | **0** | Eliminated missed transactions in `bsb-003` & `bsb-005` |
| **Precision** | **100.00%** | **100.00%** | Perfect extraction precision |
| **Recall** | 97.17% | **100.00%** | +2.83% improvement |
| **F1-Score** | 98.56% | **100.00%** | +1.44% improvement |
| **Exact Transaction-Match Accuracy** | 96.23% (102/106) | **100.00% (106/106)** | All fields (Date, Desc, Amounts, Balance) simultaneously match |
| **Balance Reconciliation Rate** | 83.3% (5/6) | **100.0% (6/6)** | Complete accounting balance integrity |
| **Average Processing Latency** | 37.0 ms | 163.5 ms | Well within 500 ms SLA for interactive document parsing |

### 4.2 Field-Level Accuracy Breakdown (Reconciled Aggregate)
| Document ID | Document Layout | Date Accuracy | Description Accuracy | Debit Amount Accuracy | Credit Amount Accuracy | Balance Accuracy |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **bsb-001** | Straits Capital (SG) | 12 / 12 (100.0%) | 12 / 12 (100.0%) | 9 / 9 (100.0%) | 3 / 3 (100.0%) | 12 / 12 (100.0%) |
| **bsb-002** | Liberty National (US) | 15 / 15 (100.0%) | 15 / 15 (100.0%) | 14 / 14 (100.0%) | 1 / 1 (100.0%) | N/A (Credit Card) |
| **bsb-003** | Continental Trust (NL) | 22 / 22 (100.0%) | 22 / 22 (100.0%) | 17 / 17 (100.0%) | 5 / 5 (100.0%) | N/A (No Line Bal) |
| **bsb-004** | Silk Road Banking (HK) | 25 / 25 (100.0%) | 25 / 25 (100.0%) | 19 / 19 (100.0%) | 6 / 6 (100.0%) | 25 / 25 (100.0%) |
| **bsb-005** | Harbour Bank (CA) | 25 / 25 (100.0%) | 25 / 25 (100.0%) | 18 / 18 (100.0%) | 7 / 7 (100.0%) | 25 / 25 (100.0%) |
| **bank_muscat**| Bank Muscat (OM - Synthetic)| 7 / 7 (100.0%) | 7 / 7 (100.0%) | 5 / 5 (100.0%) | 2 / 2 (100.0%) | 7 / 7 (100.0%) |
| **TOTAL** | **All 106 Transactions** | **106 / 106 (100.0%)**| **106 / 106 (100.0%)** | **82 / 82 (100.0%)** | **24 / 24 (100.0%)** | **69 / 69 (100.0%)** |

### 4.3 Held-Out Synthetic NLP Benchmark
To evaluate the semantic classifiers without direct training data overlap, a held-out evaluation set of **80 distinct synthetic banking narrations** (`data/evaluation/nlp_evaluation_set.json`) was generated, covering all 8 taxonomy classes (10 examples per class). None of these 80 narratives appear in the training corpus (`TRAINING_DATA`) of the models.

Evaluated using `scripts/evaluate_nlp_models.py` (results saved to `data/evaluation/nlp_benchmark_results.json`):

#### Overall Performance Summary
| Metric | scikit-learn (Production Engine) | Hugging Face Transformers (Zero-Shot) | Architectural Comparison |
| :--- | :---: | :---: | :--- |
| **Accuracy** | **83.75% (67/80)** | 41.25% (33/80) | Difference of **42.50 percentage points** |
| **Macro-Precision** | **88.59%** | 56.73% | High precision across distinct banking classes |
| **Macro-Recall** | **83.75%** | 41.25% | Low false-negative rate with domain training |
| **Macro-F1** | **84.76%** | 37.33% | Difference of 47.43 percentage points |
| **Avg Latency (CPU)** | **0.32 ms** | 104.09 ms | **scikit-learn is 325x faster** on standard CPU |
| **Offline Footprint** | **0.06 MB (Joblib)** | 255.4 MB (Safetensors) | Zero network requirement for production |

#### Per-Category Performance Breakdown
| Category | Support | scikit-learn F1 | Transformers F1 | Dominant Failure Mode in Zero-Shot |
| :--- | :---: | :---: | :---: | :--- |
| **INCOME_SALARY** | 10 | **84.21%** | 50.00% | Zero-shot confuses generic wage entries with funds transfer |
| **TRANSFER_P2P** | 10 | **95.24%** | 40.82% | Zero-shot over-predicts transfer (29 false positives) |
| **MERCHANT_POS** | 10 | 82.35% | **88.89%** | Zero-shot recognizes retail shopping brands well |
| **UTILITIES_SERVICES** | 10 | **88.89%** | 46.15% | Telecom/power charges pulled into P2P transfers |
| **ATM_CASH** | 10 | **90.00%** | 42.86% | Non-standard ATM codes (off-us, cashpoint) missed |
| **BANK_FEES** | 10 | **84.21%** | 18.18% | Commission/SWIFT fees misidentified as P2P transfers |
| **INVESTMENT_DIVIDEND**| 10 | **88.89%** | 0.00% | Coupon/distribution credits pulled into generic transfers |
| **OTHER** | 10 | **64.29%** | 11.76% | Internal sweeps/holds lack dedicated NLI hypothesis |

#### Confusion Matrix (scikit-learn Production Engine)
```
Actual \ Pred          | INCOME | TRANSF | MERCHA | UTILIT | ATM_CA | BANK_F | INVEST | OTHER 
----------------------------------------------------------------------------------------------------
INCOME_SALARY          | 8      | 0      | 0      | 0      | 0      | 1      | 0      | 1     
TRANSFER_P2P           | 0      | 10     | 0      | 0      | 0      | 0      | 0      | 0     
MERCHANT_POS           | 0      | 0      | 7      | 0      | 0      | 0      | 0      | 3     
UTILITIES_SERVICES     | 0      | 0      | 0      | 8      | 0      | 0      | 0      | 2     
ATM_CASH               | 0      | 0      | 0      | 0      | 9      | 0      | 0      | 1     
BANK_FEES              | 0      | 0      | 0      | 0      | 1      | 8      | 0      | 1     
INVESTMENT_DIVIDEND    | 1      | 0      | 0      | 0      | 0      | 0      | 8      | 1     
OTHER                  | 0      | 1      | 0      | 0      | 0      | 0      | 0      | 9     
```

#### Production Recommendation
The empirical evaluation demonstrates that the lightweight **scikit-learn** model (`TfidfVectorizer` + `LogisticRegression`) is vastly superior for production deployment:
- Operates at **0.32 ms** latency ($325\times$ faster than the Transformer).
- Reaches **83.75% accuracy** and **84.76% Macro-F1** on held-out synthetic banking narratives (an accuracy difference of 42.50 percentage points over the Transformer).
- Requires no external weight downloads or pre-cached models (0.06 MB footprint).
The Hugging Face Transformer remains an optional secondary mode (`use_transformers=True`) for deep contextual analysis where latency is not a critical constraint.

---

## 5. Technical Limitations & Operational Boundaries

1. **Scanned Images**: Operates on digital PDFs containing selectable vector text. Scanned physical documents (image-only) are detected and flagged with HTTP 200 containing clear warnings; no OCR hallucination is performed.
2. **Bank Muscat Scope**: Validated on a synthetic 7-transaction Bank Muscat PDF created from official BRD specifications. Testing against authorized, real customer production statements is required before enterprise deployment.
3. **Generalization Scope**: Reported 100% metrics on document table extraction reflect development-set performance on the 6 target layouts and should be validated against additional out-of-sample statements.
4. **Held-Out Synthetic Benchmark Status & Tuning Disclosures**:
   - The 80-example NLP benchmark suite (`data/evaluation/nlp_evaluation_set.json`) is a **held-out synthetic benchmark**, not evidence of enterprise-level generalization across production banking ledgers.
   - While the 80 narratives were kept strictly disjoint from `TRAINING_DATA` (zero string/record overlap), the candidate-label descriptions and confidence thresholds ($0.22$) were formulated during iterative development. It cannot be formally proven that label phrasing and threshold selection were established under strict double-blind isolation from developer intuition regarding typical banking descriptions. Users must treat these metrics as benchmark-sample validation rather than guaranteed out-of-distribution generalization.
5. **Zero-Shot NLI Bias**: Generic NLI models fine-tuned on MultiNLI exhibit a strong structural bias toward broad semantic concepts (e.g. "funds transfer") on banking texts because nearly all bank transactions involve the transfer of funds. Specialized domain-trained classifiers (`scikit-learn`) substantially outperform off-the-shelf zero-shot NLI models.
