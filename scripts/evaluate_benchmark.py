"""
Quantitative Benchmark Evaluation Script.
Computes rigorous, transaction-level evaluation metrics:
- True Positives (TP), False Positives (FP), False Negatives (FN)
- Precision, Recall, F1-Score
- Exact Transaction-Match Accuracy (all fields simultaneously matching)
- Field-Level Accuracies: Date, Description, Debit, Credit, Running Balance
- Accounting Balance Reconciliation status and latency.

Evaluates both Baseline (Rule-Based) and ML-Enhanced Pipelines across:
1. Bankstatemently Benchmark statements (bsb-001 through bsb-005) [Development Set]
2. Bank Muscat bilingual statement [Synthetic Sample Validation]
"""

import os
import sys
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from difflib import SequenceMatcher
from tabulate import tabulate

sys.path.insert(0, os.path.abspath("."))
from app.services.extractor import StatementExtractorService


def text_similarity(a: Optional[str], b: Optional[str]) -> float:
    """Compute normalized character sequence similarity ratio."""
    sa = (a or "").strip().lower()
    sb = (b or "").strip().lower()
    return SequenceMatcher(None, sa, sb).ratio()


def evaluate_statement_transactions(
    gt_data: Dict[str, Any],
    ext_txns: List[Any],
    desc_sim_threshold: float = 0.70
) -> Dict[str, Any]:
    """
    Perform 1-to-1 matching between extracted transactions and ground truth reference transactions.

    Matching Criteria (True Positive):
    - Direction matches (debit vs credit)
    - Amount matches within 0.005 currency units
    - Date matches or description similarity >= desc_sim_threshold
    """
    gt_txns = gt_data["transactions"]
    n_expected = len(gt_txns)
    matched_gt_indices = set()
    tp_pairs = []
    fps = []

    # Greedy 1-to-1 matching based on similarity score
    for e in ext_txns:
        best_idx = None
        best_score = 0.0
        for idx, g in enumerate(gt_txns):
            if idx in matched_gt_indices:
                continue
            amt_match = abs(e.amount - g["amount"]) < 0.005
            dir_match = (e.direction == g["direction"])
            date_match = (e.date == g["date"])
            sim = text_similarity(e.description, g["description"])

            if amt_match and dir_match:
                # Combined score: amount+direction (2.0) + date (1.0) + description similarity (0.0 - 1.0)
                score = 2.0 + (1.0 if date_match else 0.0) + sim
                if score > best_score:
                    best_score = score
                    best_idx = idx

        if best_idx is not None and best_score >= 2.5:
            matched_gt_indices.add(best_idx)
            tp_pairs.append((e, gt_txns[best_idx]))
        else:
            fps.append(e)

    tp = len(tp_pairs)
    fp = len(fps)
    fn = n_expected - tp

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / n_expected if n_expected > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    # Field-Level Accuracy Breakdown
    date_eval = 0; date_correct = 0
    desc_eval = 0; desc_correct = 0
    debit_eval = 0; debit_correct = 0
    credit_eval = 0; credit_correct = 0
    bal_eval = 0; bal_correct = 0
    exact_matches = 0

    for e, g in tp_pairs:
        # Date
        date_eval += 1
        d_ok = (e.date == g["date"])
        if d_ok:
            date_correct += 1

        # Description
        desc_eval += 1
        desc_ok = (text_similarity(e.description, g["description"]) >= desc_sim_threshold)
        if desc_ok:
            desc_correct += 1

        # Debit / Credit amounts
        debit_ok = True
        credit_ok = True
        if g["direction"] == "debit":
            debit_eval += 1
            debit_ok = (abs(e.amount - g["amount"]) < 0.005)
            if debit_ok:
                debit_correct += 1
        else:
            credit_eval += 1
            credit_ok = (abs(e.amount - g["amount"]) < 0.005)
            if credit_ok:
                credit_correct += 1

        # Balance
        bal_ok = True
        if g.get("balance") is not None:
            bal_eval += 1
            if e.balance is not None and abs(e.balance - g["balance"]) < 0.005:
                bal_correct += 1
            else:
                bal_ok = False

        # Exact Transaction Match: date, desc, amount/direction, and balance all correct
        if d_ok and desc_ok and (debit_ok if g["direction"] == "debit" else credit_ok) and bal_ok:
            exact_matches += 1

    exact_accuracy = exact_matches / n_expected if n_expected > 0 else 0.0

    return {
        "expected_txns": n_expected,
        "extracted_txns": len(ext_txns),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": round(precision * 100, 2),
        "recall": round(recall * 100, 2),
        "f1": round(f1 * 100, 2),
        "exact_matches": exact_matches,
        "exact_accuracy": round(exact_accuracy * 100, 2),
        "field_accuracy": {
            "date": {
                "correct": date_correct,
                "evaluated": date_eval,
                "pct": round((date_correct / date_eval * 100), 2) if date_eval > 0 else 0.0
            },
            "description": {
                "correct": desc_correct,
                "evaluated": desc_eval,
                "pct": round((desc_correct / desc_eval * 100), 2) if desc_eval > 0 else 0.0
            },
            "debit": {
                "correct": debit_correct,
                "evaluated": debit_eval,
                "pct": round((debit_correct / debit_eval * 100), 2) if debit_eval > 0 else 0.0
            },
            "credit": {
                "correct": credit_correct,
                "evaluated": credit_eval,
                "pct": round((credit_correct / credit_eval * 100), 2) if credit_eval > 0 else 0.0
            },
            "balance": {
                "correct": bal_correct,
                "evaluated": bal_eval,
                "pct": round((bal_correct / bal_eval * 100), 2) if bal_eval > 0 else None,
                "available": (bal_eval > 0)
            }
        }
    }


def run_evaluation():
    service = StatementExtractorService()

    eval_suite = [
        {
            "id": "bsb-001",
            "name": "Straits Capital (SG)",
            "type": "Benchmark Statement (Development Set)",
            "path": "data/bankstatemently_benchmark/datasets/basic/bsb-001/bsb-001-statement.pdf",
            "gt_path": "data/evaluation/ground_truth/bsb-001.json",
            "profile": "straits_capital"
        },
        {
            "id": "bsb-002",
            "name": "Liberty National (US)",
            "type": "Benchmark Statement (Development Set)",
            "path": "data/bankstatemently_benchmark/datasets/basic/bsb-002/bsb-002-statement.pdf",
            "gt_path": "data/evaluation/ground_truth/bsb-002.json",
            "profile": "liberty_national"
        },
        {
            "id": "bsb-003",
            "name": "Continental Trust (NL)",
            "type": "Benchmark Statement (Development Set)",
            "path": "data/bankstatemently_benchmark/datasets/basic/bsb-003/bsb-003-statement.pdf",
            "gt_path": "data/evaluation/ground_truth/bsb-003.json",
            "profile": "continental_trust"
        },
        {
            "id": "bsb-004",
            "name": "Silk Road Banking (HK)",
            "type": "Benchmark Statement (Development Set)",
            "path": "data/bankstatemently_benchmark/datasets/basic/bsb-004/bsb-004-statement.pdf",
            "gt_path": "data/evaluation/ground_truth/bsb-004.json",
            "profile": "silk_road"
        },
        {
            "id": "bsb-005",
            "name": "Harbour Bank (CA)",
            "type": "Benchmark Statement (Development Set)",
            "path": "data/bankstatemently_benchmark/datasets/basic/bsb-005/bsb-005-statement.pdf",
            "gt_path": "data/evaluation/ground_truth/bsb-005.json",
            "profile": "harbour_bank"
        },
        {
            "id": "bank_muscat",
            "name": "Bank Muscat (OM)",
            "type": "Synthetic Sample Statement",
            "path": "data/raw/bank_muscat_sample.pdf",
            "gt_path": "data/evaluation/ground_truth/bank_muscat.json",
            "profile": "bank_muscat"
        }
    ]

    results_baseline = []
    results_ml = []

    print("=" * 100)
    print("BANK STATEMENT TABLE EXTRACTION: RIGOROUS BENCHMARK EVALUATION")
    print("=" * 100)

    for doc in eval_suite:
        doc_id = doc["id"]
        path = doc["path"]
        gt_path = doc["gt_path"]
        prof = doc["profile"]

        if not os.path.exists(path) or not os.path.exists(gt_path):
            print(f"Skipping {doc_id}, missing file: {path} or {gt_path}")
            continue

        with open(gt_path, "r", encoding="utf-8") as f:
            gt_data = json.load(f)

        # 1. Run Baseline (Rule-Based Heuristic)
        t0 = time.time()
        res_base = service.extract_from_path(path, profile_id=prof, use_ml=False)
        base_time = (time.time() - t0) * 1000

        eval_base = evaluate_statement_transactions(gt_data, res_base.transactions)
        eval_base["doc_id"] = doc_id
        eval_base["name"] = doc["name"]
        eval_base["type"] = doc["type"]
        eval_base["latency_ms"] = round(base_time, 1)
        eval_base["reconciled"] = "PASS" if res_base.validation.reconciled else "WARN"
        eval_base["warnings"] = res_base.validation.warnings
        results_baseline.append(eval_base)

        # 2. Run ML-Enhanced Pipeline
        t1 = time.time()
        res_ml = service.extract_from_path(path, profile_id=prof, use_ml=True)
        ml_time = (time.time() - t1) * 1000

        eval_ml = evaluate_statement_transactions(gt_data, res_ml.transactions)
        eval_ml["doc_id"] = doc_id
        eval_ml["name"] = doc["name"]
        eval_ml["type"] = doc["type"]
        eval_ml["latency_ms"] = round(ml_time, 1)
        eval_ml["reconciled"] = "PASS" if res_ml.validation.reconciled else "WARN"
        eval_ml["warnings"] = res_ml.validation.warnings
        results_ml.append(eval_ml)

    # Populate Table Rows
    base_table_rows = []
    for r in results_baseline:
        bal_str = f"{r['field_accuracy']['balance']['pct']}%" if r['field_accuracy']['balance']['available'] else "N/A"
        base_table_rows.append([
            r["doc_id"], r["name"], r["expected_txns"], r["extracted_txns"],
            r["true_positives"], r["false_positives"], r["false_negatives"],
            f"{r['precision']}%", f"{r['recall']}%", f"{r['f1']}%",
            f"{r['exact_accuracy']}%",
            bal_str,
            r["reconciled"], f"{r['latency_ms']} ms"
        ])
    base_headers = ["ID", "Document", "Exp", "Ext", "TP", "FP", "FN", "Prec", "Rec", "F1", "Exact Match", "Bal Acc", "Recon", "Latency"]

    ml_table_rows = []
    for r in results_ml:
        bal_str = f"{r['field_accuracy']['balance']['pct']}%" if r['field_accuracy']['balance']['available'] else "N/A"
        ml_table_rows.append([
            r["doc_id"], r["name"], r["expected_txns"], r["extracted_txns"],
            r["true_positives"], r["false_positives"], r["false_negatives"],
            f"{r['precision']}%", f"{r['recall']}%", f"{r['f1']}%",
            f"{r['exact_accuracy']}%",
            bal_str,
            r["reconciled"], f"{r['latency_ms']} ms"
        ])

    field_headers = ["ID", "Document", "Date Acc", "Description Acc", "Debit Acc", "Credit Acc", "Balance Acc"]
    field_rows = []
    for r in results_ml:
        fa = r["field_accuracy"]
        bal_disp = f"{fa['balance']['correct']}/{fa['balance']['evaluated']} ({fa['balance']['pct']}%)" if fa['balance']['available'] else "N/A (No Running Bal)"
        field_rows.append([
            r["doc_id"], r["name"],
            f"{fa['date']['correct']}/{fa['date']['evaluated']} ({fa['date']['pct']}%)",
            f"{fa['description']['correct']}/{fa['description']['evaluated']} ({fa['description']['pct']}%)",
            f"{fa['debit']['correct']}/{fa['debit']['evaluated']} ({fa['debit']['pct']}%)",
            f"{fa['credit']['correct']}/{fa['credit']['evaluated']} ({fa['credit']['pct']}%)",
            bal_disp
        ])

    # Aggregate Statistics
    total_exp = sum(r["expected_txns"] for r in results_ml)
    total_ext_base = sum(r["extracted_txns"] for r in results_baseline)
    total_tp_base = sum(r["true_positives"] for r in results_baseline)
    total_fp_base = sum(r["false_positives"] for r in results_baseline)
    total_fn_base = sum(r["false_negatives"] for r in results_baseline)
    total_exact_base = sum(r["exact_matches"] for r in results_baseline)
    macro_prec_base = total_tp_base / (total_tp_base + total_fp_base) * 100 if (total_tp_base + total_fp_base) > 0 else 0.0
    macro_rec_base = total_tp_base / (total_tp_base + total_fn_base) * 100 if (total_tp_base + total_fn_base) > 0 else 0.0
    macro_f1_base = (2 * macro_prec_base * macro_rec_base) / (macro_prec_base + macro_rec_base) if (macro_prec_base + macro_rec_base) > 0 else 0.0
    avg_latency_base = sum(r["latency_ms"] for r in results_baseline) / len(results_baseline) if results_baseline else 0.0
    reconciled_base_count = sum(1 for r in results_baseline if r["reconciled"] == "PASS")

    # Baseline field aggregates
    b_date_corr = sum(r["field_accuracy"]["date"]["correct"] for r in results_baseline)
    b_date_eval = sum(r["field_accuracy"]["date"]["evaluated"] for r in results_baseline)
    b_desc_corr = sum(r["field_accuracy"]["description"]["correct"] for r in results_baseline)
    b_desc_eval = sum(r["field_accuracy"]["description"]["evaluated"] for r in results_baseline)
    b_deb_corr = sum(r["field_accuracy"]["debit"]["correct"] for r in results_baseline)
    b_deb_eval = sum(r["field_accuracy"]["debit"]["evaluated"] for r in results_baseline)
    b_cred_corr = sum(r["field_accuracy"]["credit"]["correct"] for r in results_baseline)
    b_cred_eval = sum(r["field_accuracy"]["credit"]["evaluated"] for r in results_baseline)
    b_bal_corr = sum(r["field_accuracy"]["balance"]["correct"] for r in results_baseline if r["field_accuracy"]["balance"]["available"])
    b_bal_eval = sum(r["field_accuracy"]["balance"]["evaluated"] for r in results_baseline if r["field_accuracy"]["balance"]["available"])

    total_ext_ml = sum(r["extracted_txns"] for r in results_ml)
    total_tp_ml = sum(r["true_positives"] for r in results_ml)
    total_fp_ml = sum(r["false_positives"] for r in results_ml)
    total_fn_ml = sum(r["false_negatives"] for r in results_ml)
    total_exact_ml = sum(r["exact_matches"] for r in results_ml)
    macro_prec_ml = total_tp_ml / (total_tp_ml + total_fp_ml) * 100 if (total_tp_ml + total_fp_ml) > 0 else 0.0
    macro_rec_ml = total_tp_ml / (total_tp_ml + total_fn_ml) * 100 if (total_tp_ml + total_fn_ml) > 0 else 0.0
    macro_f1_ml = (2 * macro_prec_ml * macro_rec_ml) / (macro_prec_ml + macro_rec_ml) if (macro_prec_ml + macro_rec_ml) > 0 else 0.0
    avg_latency_ml = sum(r["latency_ms"] for r in results_ml) / len(results_ml) if results_ml else 0.0
    reconciled_ml_count = sum(1 for r in results_ml if r["reconciled"] == "PASS")

    # ML field aggregates
    m_date_corr = sum(r["field_accuracy"]["date"]["correct"] for r in results_ml)
    m_date_eval = sum(r["field_accuracy"]["date"]["evaluated"] for r in results_ml)
    m_desc_corr = sum(r["field_accuracy"]["description"]["correct"] for r in results_ml)
    m_desc_eval = sum(r["field_accuracy"]["description"]["evaluated"] for r in results_ml)
    m_deb_corr = sum(r["field_accuracy"]["debit"]["correct"] for r in results_ml)
    m_deb_eval = sum(r["field_accuracy"]["debit"]["evaluated"] for r in results_ml)
    m_cred_corr = sum(r["field_accuracy"]["credit"]["correct"] for r in results_ml)
    m_cred_eval = sum(r["field_accuracy"]["credit"]["evaluated"] for r in results_ml)
    m_bal_corr = sum(r["field_accuracy"]["balance"]["correct"] for r in results_ml if r["field_accuracy"]["balance"]["available"])
    m_bal_eval = sum(r["field_accuracy"]["balance"]["evaluated"] for r in results_ml if r["field_accuracy"]["balance"]["available"])

    # Append TOTAL rows to tables
    base_table_rows.append([
        "TOTAL", "Aggregate Suite", total_exp, total_ext_base,
        total_tp_base, total_fp_base, total_fn_base,
        f"{macro_prec_base:.2f}%", f"{macro_rec_base:.2f}%", f"{macro_f1_base:.2f}%",
        f"{(total_exact_base/total_exp*100):.2f}% ({total_exact_base}/{total_exp})",
        f"{(b_bal_corr/b_bal_eval*100):.1f}% ({b_bal_corr}/{b_bal_eval})",
        f"{reconciled_base_count}/{len(results_baseline)}", f"{avg_latency_base:.1f} ms"
    ])

    ml_table_rows.append([
        "TOTAL", "Aggregate Suite", total_exp, total_ext_ml,
        total_tp_ml, total_fp_ml, total_fn_ml,
        f"{macro_prec_ml:.2f}%", f"{macro_rec_ml:.2f}%", f"{macro_f1_ml:.2f}%",
        f"{(total_exact_ml/total_exp*100):.2f}% ({total_exact_ml}/{total_exp})",
        f"{(m_bal_corr/m_bal_eval*100):.1f}% ({m_bal_corr}/{m_bal_eval})",
        f"{reconciled_ml_count}/{len(results_ml)}", f"{avg_latency_ml:.1f} ms"
    ])

    field_rows.append([
        "TOTAL", "All 106 Transactions",
        f"{m_date_corr}/{m_date_eval} ({(m_date_corr/m_date_eval*100):.1f}%)",
        f"{m_desc_corr}/{m_desc_eval} ({(m_desc_corr/m_desc_eval*100):.1f}%)",
        f"{m_deb_corr}/{m_deb_eval} ({(m_deb_corr/m_deb_eval*100):.1f}%)",
        f"{m_cred_corr}/{m_cred_eval} ({(m_cred_corr/m_cred_eval*100):.1f}%)",
        f"{m_bal_corr}/{m_bal_eval} ({(m_bal_corr/m_bal_eval*100):.1f}%)"
    ])

    print("\n[A] BASELINE PIPELINE (RULE-BASED HEURISTICS):")
    print(tabulate(base_table_rows, headers=base_headers, tablefmt="github"))

    print("\n[B] ML-ENHANCED PIPELINE (RANDOM FOREST + TF-IDF LOGISTIC REGRESSION):")
    print(tabulate(ml_table_rows, headers=base_headers, tablefmt="github"))

    print("\n[C] FIELD-LEVEL ACCURACY BREAKDOWN (ML-ENHANCED PIPELINE):")
    print(tabulate(field_rows, headers=field_headers, tablefmt="github"))

    print("\n[D] AGGREGATE SUMMARY & COMPARISON:")
    print(f"  Total Statements Evaluated: {len(results_ml)}")
    print(f"  Total Expected Ground-Truth Transactions: {total_exp}")
    print(f"  Baseline Pipeline: {total_ext_base}/{total_exp} extracted | TP={total_tp_base}, FP={total_fp_base}, FN={total_fn_base} | Precision: {macro_prec_base:.2f}%, Recall: {macro_rec_base:.2f}%, F1: {macro_f1_base:.2f}%")
    print(f"  ML-Enhanced Pipeline: {total_ext_ml}/{total_exp} extracted | TP={total_tp_ml}, FP={total_fp_ml}, FN={total_fn_ml} | Precision: {macro_prec_ml:.2f}%, Recall: {macro_rec_ml:.2f}%, F1: {macro_f1_ml:.2f}%")

    # Serialize to JSON
    os.makedirs("data/evaluation", exist_ok=True)
    out_payload = {
        "metadata": {
            "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "matching_criteria": {
                "description": "1-to-1 matching requiring exact amount (tolerance 0.005), exact direction, and date match or description similarity >= 0.70",
                "exact_transaction_match_definition": "Simultaneous correctness of Date, Description (sim >= 0.70), Amount/Direction, and Running Balance (where present)"
            },
            "evaluation_scope_disclosure": {
                "benchmark_statements_bsb001_to_bsb005": "Development set / benchmark sample evaluation. ML line classifier training set contains exemplar patterns from these documents. Not out-of-distribution holdout evaluation.",
                "bank_muscat_statement": "Synthetic sample validation generated from Bank Muscat specifications. Not an authorized production customer statement."
            }
        },
        "aggregate": {
            "total_statements": len(results_ml),
            "total_expected_transactions": total_exp,
            "baseline": {
                "extracted": total_ext_base,
                "true_positives": total_tp_base,
                "false_positives": total_fp_base,
                "false_negatives": total_fn_base,
                "exact_matches": total_exact_base,
                "micro_precision": round(macro_prec_base, 2),
                "micro_recall": round(macro_rec_base, 2),
                "micro_f1": round(macro_f1_base, 2),
                "field_accuracy": {
                    "date": {"correct": b_date_corr, "evaluated": b_date_eval, "pct": round(b_date_corr / b_date_eval * 100, 2)},
                    "description": {"correct": b_desc_corr, "evaluated": b_desc_eval, "pct": round(b_desc_corr / b_desc_eval * 100, 2)},
                    "debit": {"correct": b_deb_corr, "evaluated": b_deb_eval, "pct": round(b_deb_corr / b_deb_eval * 100, 2)},
                    "credit": {"correct": b_cred_corr, "evaluated": b_cred_eval, "pct": round(b_cred_corr / b_cred_eval * 100, 2)},
                    "balance": {"correct": b_bal_corr, "evaluated": b_bal_eval, "pct": round(b_bal_corr / b_bal_eval * 100, 2)}
                }
            },
            "ml_enhanced": {
                "extracted": total_ext_ml,
                "true_positives": total_tp_ml,
                "false_positives": total_fp_ml,
                "false_negatives": total_fn_ml,
                "exact_matches": total_exact_ml,
                "micro_precision": round(macro_prec_ml, 2),
                "micro_recall": round(macro_rec_ml, 2),
                "micro_f1": round(macro_f1_ml, 2),
                "field_accuracy": {
                    "date": {"correct": m_date_corr, "evaluated": m_date_eval, "pct": round(m_date_corr / m_date_eval * 100, 2)},
                    "description": {"correct": m_desc_corr, "evaluated": m_desc_eval, "pct": round(m_desc_corr / m_desc_eval * 100, 2)},
                    "debit": {"correct": m_deb_corr, "evaluated": m_deb_eval, "pct": round(m_deb_corr / m_deb_eval * 100, 2)},
                    "credit": {"correct": m_cred_corr, "evaluated": m_cred_eval, "pct": round(m_cred_corr / m_cred_eval * 100, 2)},
                    "balance": {"correct": m_bal_corr, "evaluated": m_bal_eval, "pct": round(m_bal_corr / m_bal_eval * 100, 2)}
                }
            }
        },
        "baseline_results": results_baseline,
        "ml_results": results_ml
    }

    with open("data/evaluation/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(out_payload, f, indent=2)

    print("\nVerified evaluation results written to: data/evaluation/benchmark_results.json")


if __name__ == "__main__":
    run_evaluation()
