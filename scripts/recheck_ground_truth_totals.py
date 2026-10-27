import json
import glob
from pathlib import Path

def main():
    gt_dir = Path("data/evaluation/ground_truth")
    gt_files = sorted(gt_dir.glob("*.json"))
    
    print("=" * 80)
    print("GROUND TRUTH TRANSACTION RECONCILIATION AUDIT")
    print("=" * 80)
    print(f"{'File Name':<20} | {'Total Tx':<10} | {'Debits':<8} | {'Credits':<8} | {'Balances':<10}")
    print("-" * 80)
    
    grand_total = 0
    grand_debit = 0
    grand_credit = 0
    grand_balance = 0
    
    for f in gt_files:
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        
        txs = data.get("transactions", [])
        total_tx = len(txs)
        debits = sum(1 for t in txs if t.get("direction") == "debit")
        credits = sum(1 for t in txs if t.get("direction") == "credit")
        balances = sum(1 for t in txs if t.get("balance") is not None)
        
        grand_total += total_tx
        grand_debit += debits
        grand_credit += credits
        grand_balance += balances
        
        print(f"{f.name:<20} | {total_tx:<10} | {debits:<8} | {credits:<8} | {balances:<10}")
        
    print("=" * 80)
    print(f"{'TOTAL AGGREGATE':<20} | {grand_total:<10} | {grand_debit:<8} | {grand_credit:<8} | {grand_balance:<10}")
    print("=" * 80)
    
    # Assertions
    assert grand_total == 106, f"Expected 106 total transactions, got {grand_total}"
    assert grand_debit == 82, f"Expected 82 debits, got {grand_debit}"
    assert grand_credit == 24, f"Expected 24 credits, got {grand_credit}"
    assert grand_balance == 69, f"Expected 69 stated balances, got {grand_balance}"
    print("\nALL RECONCILIATION ASSERTIONS PASSED:")
    print(f"  - Total Transactions: {grand_total} (Expected: 106)")
    print(f"  - Total Debits: {grand_debit} (Expected: 82)")
    print(f"  - Total Credits: {grand_credit} (Expected: 24)")
    print(f"  - Stated Balances: {grand_balance} (Expected: 69)")
    print(f"  - Debits + Credits == Total: {grand_debit + grand_credit == grand_total}")

if __name__ == "__main__":
    main()
