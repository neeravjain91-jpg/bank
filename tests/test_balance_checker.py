"""
Unit tests for accounting validation and balance reconciliation.
"""

import pytest
from app.schemas.transaction import Transaction
from app.validation.balance_checker import validate_statement_balances


def test_balance_reconciliation_pass():
    txns = [
        Transaction(date="2025-01-01", description="Deposit", amount=100.0, direction="credit", balance=1100.0),
        Transaction(date="2025-01-02", description="Withdrawal", amount=50.0, direction="debit", balance=1050.0),
        Transaction(date="2025-01-03", description="Coffee", amount=10.0, direction="debit", balance=1040.0),
    ]
    res = validate_statement_balances(
        transactions=txns,
        opening_balance=1000.0,
        reported_closing_balance=1040.0
    )
    assert res.reconciled is True
    assert res.discrepancy_count == 0
    assert res.total_credits == 100.0
    assert res.total_debits == 60.0
    assert res.net_change == 40.0


def test_balance_reconciliation_discrepancy_detected():
    # Transaction 2 has an incorrect balance of 1020 instead of 1050
    txns = [
        Transaction(date="2025-01-01", description="Deposit", amount=100.0, direction="credit", balance=1100.0),
        Transaction(date="2025-01-02", description="Withdrawal", amount=50.0, direction="debit", balance=1020.0),
    ]
    res = validate_statement_balances(
        transactions=txns,
        opening_balance=1000.0,
        reported_closing_balance=1050.0
    )
    assert res.reconciled is False
    assert res.discrepancy_count == 1
    assert len(res.discrepancies) == 1
    assert res.discrepancies[0]["difference"] == -30.0


def test_credit_card_balance_rule():
    # In credit card, debit = charge (+balance), credit = payment (-balance)
    txns = [
        Transaction(date="2025-09-01", description="UBER", amount=50.0, direction="debit", balance=550.0),
        Transaction(date="2025-09-02", description="PAYMENT", amount=200.0, direction="credit", balance=350.0),
    ]
    res = validate_statement_balances(
        transactions=txns,
        opening_balance=500.0,
        reported_closing_balance=350.0,
        account_type="credit_card"
    )
    assert res.reconciled is True
    assert res.discrepancy_count == 0
