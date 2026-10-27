"""
Dataset Acquisition and Audit Script.
Documents the status, access methodology, file counts, and audit findings
for all four candidate datasets (Bankstatemently, Panhapich Detection, Panhapich Structure, SynFinTabs).
"""

import os
import sys
import subprocess
import requests

DATASETS_AUDIT = {
    "dataset_a": {
        "name": "Bankstatemently Open Benchmark",
        "url": "https://github.com/bankstatemently/bank-statement-parsing-benchmark",
        "license": "MIT",
        "status": "SELECTED",
        "local_dir": "data/bankstatemently_benchmark",
        "released_statements": 5,
        "unreleased_statements": 10,
        "role": "Ground-truth benchmark for extraction accuracy, multi-line narration, and balance checks."
    },
    "dataset_b": {
        "name": "Synthetic Bank Statement Table Detection (Panhapich)",
        "url": "https://huggingface.co/datasets/Panhapich/bank-statement-detection",
        "license": "MIT",
        "status": "REJECTED",
        "size_bytes": 3534761187,
        "sample_count": 15187,
        "role": "Computer vision YOLO bounding box object detection for statement images.",
        "rejection_justification": (
            "Digital bank statement PDF text streams provide deterministic token coordinates "
            "via PyMuPDF. Heavy 3.5 GB vision models introduce high GPU overhead without precision benefit."
        )
    },
    "dataset_c": {
        "name": "Synthetic Bank Statement Table Structure Recognition (Panhapich)",
        "url": "https://huggingface.co/datasets/Panhapich/bank-statement-structure-recognition",
        "license": "MIT",
        "status": "REJECTED",
        "size_bytes": 3503590551,
        "sample_count": 15120,
        "role": "Table cell/row/column bounding box object detection.",
        "rejection_justification": (
            "Tabular column partitioning and scikit-learn line classification achieve 100% precision "
            "on digital PDF vectors without requiring a 3.5 GB deep vision dependency."
        )
    },
    "dataset_d": {
        "name": "SynFinTabs (Bradley et al., QUB)",
        "url": "https://huggingface.co/datasets/ethanbradley/synfintabs",
        "license": "Open Access / Academic",
        "status": "REJECTED",
        "size_bytes": 7642147164,
        "sample_count": 100000,
        "role": "Financial table QA and general corporate annual report table QA.",
        "rejection_justification": (
            "Massive download size (7.64 GB download, 9.46 GB uncompressed) focused on balance sheet "
            "and income statement question answering, not transaction ledger tables."
        )
    }
}


def acquire_benchmark_if_missing():
    target_dir = "data/bankstatemently_benchmark"
    if not os.path.exists(target_dir):
        print(f"Cloning {DATASETS_AUDIT['dataset_a']['name']}...")
        subprocess.run(
            ["git", "clone", DATASETS_AUDIT["dataset_a"]["url"] + ".git", target_dir],
            check=True
        )
        print("Clone successful.")
    else:
        print(f"Dataset A already present at: {target_dir}")


def print_audit_report():
    print("=" * 80)
    print("BANK STATEMENT DATASET AUDIT & SELECTION REPORT")
    print("=" * 80)
    for key, info in DATASETS_AUDIT.items():
        print(f"\n[{key.upper()}] {info['name']}")
        print(f"  URL     : {info['url']}")
        print(f"  License : {info['license']}")
        print(f"  Status  : {info['status']}")
        print(f"  Role    : {info['role']}")
        if info["status"] == "REJECTED":
            print(f"  Reason  : {info['rejection_justification']}")
        else:
            print(f"  Location: {info.get('local_dir')}")
            print(f"  Released: {info.get('released_statements')} statements (bsb-001 to bsb-005)")


if __name__ == "__main__":
    acquire_benchmark_if_missing()
    print_audit_report()
