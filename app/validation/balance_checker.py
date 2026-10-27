"""
Accounting validation and balance reconciliation module.
Verifies running balances and overall balance integrity across statement accounts.
Supports multi-account statements by performing reconciliation per account.
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict
from app.schemas.transaction import Transaction, BalanceValidationResult


def validate_statement_balances(
    transactions: List[Transaction],
    opening_balance: Optional[float] = None,
    reported_closing_balance: Optional[float] = None,
    account_type: str = "deposit"  # "deposit" or "credit_card"
) -> BalanceValidationResult:
    """
    Perform accounting reconciliation over extracted transactions.
    Groups by account_id for multi-account statements.
    """
    if not transactions:
        return BalanceValidationResult(
            reconciled=True,
            total_debits=0.0,
            total_credits=0.0,
            net_change=0.0,
            discrepancy_count=0
        )

    # Group by account if multi-account present
    accounts_txns = defaultdict(list)
    for txn in transactions:
        acc_key = txn.account_id or "primary"
        accounts_txns[acc_key].append(txn)

    total_debits = 0.0
    total_credits = 0.0
    all_discrepancies: List[Dict[str, Any]] = []
    warnings: List[str] = []

    for acc_id, txns in accounts_txns.items():
        prev_balance = None
        for idx, txn in enumerate(txns):
            if txn.direction == "debit":
                total_debits += txn.amount
            elif txn.direction == "credit":
                total_credits += txn.amount

            current_balance = txn.balance
            if current_balance is not None and prev_balance is not None:
                if account_type == "credit_card":
                    expected = round(prev_balance + (txn.amount if txn.direction == "debit" else -txn.amount), 2)
                else:
                    expected = round(prev_balance + (txn.amount if txn.direction == "credit" else -txn.amount), 2)
                
                actual = round(current_balance, 2)
                if abs(actual - expected) > 0.01:
                    all_discrepancies.append({
                        "account_id": acc_id,
                        "row_index": idx,
                        "date": txn.date,
                        "description": txn.description,
                        "amount": txn.amount,
                        "direction": txn.direction,
                        "previous_balance": prev_balance,
                        "expected_balance": expected,
                        "actual_balance": actual,
                        "difference": round(actual - expected, 2)
                    })
            if current_balance is not None:
                prev_balance = current_balance

    total_debits = round(total_debits, 3)
    total_credits = round(total_credits, 3)
    net_change = round(total_credits - total_debits, 3)

    calculated_closing = None
    if opening_balance is not None and len(accounts_txns) == 1:
        if account_type == "credit_card":
            calculated_closing = round(opening_balance + total_debits - total_credits, 2)
        else:
            calculated_closing = round(opening_balance + total_credits - total_debits, 2)
        
        if reported_closing_balance is not None:
            if abs(round(reported_closing_balance, 2) - calculated_closing) > 0.02:
                msg = (
                    f"Closing balance mismatch: reported={reported_closing_balance:.2f}, "
                    f"calculated={calculated_closing:.2f} (diff={abs(reported_closing_balance - calculated_closing):.2f})"
                )
                warnings.append(msg)

    if all_discrepancies:
        warnings.append(f"{len(all_discrepancies)} running balance step discrepancies detected.")

    is_reconciled = (len(all_discrepancies) == 0 and len(warnings) == 0)

    return BalanceValidationResult(
        reconciled=is_reconciled,
        opening_balance=opening_balance,
        closing_balance=reported_closing_balance,
        calculated_closing_balance=calculated_closing,
        total_debits=total_debits,
        total_credits=total_credits,
        net_change=net_change,
        discrepancy_count=len(all_discrepancies),
        discrepancies=all_discrepancies,
        warnings=warnings
    )
