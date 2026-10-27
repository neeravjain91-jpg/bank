import os
import sys
import time
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath("."))

os.environ["HF_HUB_DISABLE_XET"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from app.models.nlp_categorizer import NLPCategorizer, CATEGORIES

def evaluate_model(categorizer: NLPCategorizer, eval_data: List[Dict[str, str]], use_transformers: bool):
    engine_name = f"Hugging Face Transformers ({categorizer.hf_model_name})" if use_transformers else "scikit-learn (TF-IDF + LogisticRegression)"
    print(f"\nEvaluating: {engine_name}...")
    
    # Pre-load pipeline to measure pure inference latency
    if use_transformers and categorizer.hf_pipeline is None:
        categorizer.load_transformers_pipeline()
    
    y_true = []
    y_pred = []
    latencies = []
    details = []

    t_start_total = time.time()
    for item in eval_data:
        desc = item["description"]
        expected = item["category"]
        
        t0 = time.time()
        predicted, conf, entities = categorizer.categorize(desc, use_transformers=use_transformers)
        dt_ms = (time.time() - t0) * 1000.0
        
        y_true.append(expected)
        y_pred.append(predicted)
        latencies.append(dt_ms)
        details.append({
            "id": item["id"],
            "description": desc,
            "expected": expected,
            "predicted": predicted,
            "confidence": conf,
            "latency_ms": round(dt_ms, 2),
            "correct": predicted == expected
        })
    total_time_s = time.time() - t_start_total

    # Metrics calculation
    total = len(y_true)
    correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
    accuracy = (correct / total) * 100.0
    avg_latency = sum(latencies) / len(latencies)

    # Confusion matrix
    conf_matrix = {c_true: {c_pred: 0 for c_pred in CATEGORIES} for c_true in CATEGORIES}
    for yt, yp in zip(y_true, y_pred):
        conf_matrix[yt][yp] += 1

    # Per-category metrics
    cat_metrics = {}
    precisions = []
    recalls = []
    f1s = []

    for cat in CATEGORIES:
        tp = conf_matrix[cat][cat]
        fp = sum(conf_matrix[other][cat] for other in CATEGORIES if other != cat)
        fn = sum(conf_matrix[cat][other] for other in CATEGORIES if other != cat)
        
        prec = (tp / (tp + fp)) * 100.0 if (tp + fp) > 0 else 0.0
        rec = (tp / (tp + fn)) * 100.0 if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        
        cat_metrics[cat] = {
            "support": tp + fn,
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": round(prec, 2),
            "recall": round(rec, 2),
            "f1_score": round(f1, 2)
        }
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)

    macro_precision = sum(precisions) / len(CATEGORIES)
    macro_recall = sum(recalls) / len(CATEGORIES)
    macro_f1 = sum(f1s) / len(CATEGORIES)

    return {
        "engine": engine_name,
        "total_evaluated": total,
        "correct": correct,
        "accuracy": round(accuracy, 2),
        "macro_precision": round(macro_precision, 2),
        "macro_recall": round(macro_recall, 2),
        "macro_f1": round(macro_f1, 2),
        "avg_latency_ms": round(avg_latency, 2),
        "total_time_seconds": round(total_time_s, 2),
        "category_metrics": cat_metrics,
        "confusion_matrix": conf_matrix,
        "predictions": details
    }

def print_report(res: Dict[str, Any]):
    print("=" * 100)
    print(f"EVALUATION REPORT: {res['engine']}")
    print(f"Total Evaluated: {res['total_evaluated']} | Accuracy: {res['accuracy']}% ({res['correct']}/{res['total_evaluated']})")
    print(f"Macro Precision: {res['macro_precision']}% | Macro Recall: {res['macro_recall']}% | Macro F1: {res['macro_f1']}%")
    print(f"Avg CPU Inference Latency: {res['avg_latency_ms']} ms/txn (Total time: {res['total_time_seconds']}s)")
    print("-" * 100)
    print(f"{'Category':<22} | {'Support':<8} | {'TP':<4} | {'FP':<4} | {'FN':<4} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10}")
    print("-" * 100)
    for cat, m in res["category_metrics"].items():
        print(f"{cat:<22} | {m['support']:<8} | {m['tp']:<4} | {m['fp']:<4} | {m['fn']:<4} | {m['precision']:<9.2f}% | {m['recall']:<9.2f}% | {m['f1_score']:<9.2f}%")
    print("-" * 100)
    
    print("\nConfusion Matrix (Rows = Actual, Columns = Predicted):")
    headers = [c[:6] for c in CATEGORIES]
    title_col = "Actual \\ Pred"
    print(f"{title_col:<22} | " + " | ".join(f"{h:<6}" for h in headers))
    print("-" * 100)
    for actual in CATEGORIES:
        row = [f"{res['confusion_matrix'][actual][pred]:<6}" for pred in CATEGORIES]
        print(f"{actual:<22} | " + " | ".join(row))
    print("=" * 100)

def main():
    eval_file = Path("data/evaluation/nlp_evaluation_set.json")
    if not eval_file.exists():
        print(f"Evaluation file {eval_file} not found.")
        sys.exit(1)
        
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_payload = json.load(f)
    eval_data = eval_payload["examples"]

    categorizer = NLPCategorizer()

    # 1. Evaluate scikit-learn
    skl_results = evaluate_model(categorizer, eval_data, use_transformers=False)
    print_report(skl_results)

    # 2. Evaluate Hugging Face Transformers
    hf_results = evaluate_model(categorizer, eval_data, use_transformers=True)
    print_report(hf_results)

    # 3. Save comparative benchmark artifact
    out_payload = {
        "metadata": {
            "evaluation_dataset": eval_payload.get("dataset_name"),
            "total_examples": len(eval_data),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "categories": CATEGORIES
        },
        "scikit_learn": skl_results,
        "transformers": hf_results,
        "comparative_summary": {
            "accuracy_scikit_learn": skl_results["accuracy"],
            "accuracy_transformers": hf_results["accuracy"],
            "macro_f1_scikit_learn": skl_results["macro_f1"],
            "macro_f1_transformers": hf_results["macro_f1"],
            "avg_latency_ms_scikit_learn": skl_results["avg_latency_ms"],
            "avg_latency_ms_transformers": hf_results["avg_latency_ms"],
            "latency_ratio": round(hf_results["avg_latency_ms"] / (skl_results["avg_latency_ms"] + 1e-6), 1)
        }
    }

    out_file = Path("data/evaluation/nlp_benchmark_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(out_payload, f, indent=2)
    print(f"\nSaved full comparative evaluation results to: {out_file}")

if __name__ == "__main__":
    main()
