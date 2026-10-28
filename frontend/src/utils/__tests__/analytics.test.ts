import { describe, it, expect } from 'vitest'
import {
  calculateFinancialSummary,
  calculateCategoryBreakdown,
  calculateDailyCashFlow,
  calculateTopOutflowMerchants,
} from '../analytics'
import { Transaction, BalanceValidationResult } from '../../types'

describe('Analytics Utility Tests', () => {
  const sampleTransactions: Transaction[] = [
    {
      date: '2024-03-01',
      description: 'SALARY CREDIT ACME CORP',
      amount: 800.0,
      direction: 'credit',
      currency: 'OMR',
      balance: 1800.0,
      category: 'SALARY',
    },
    {
      date: '2024-03-02',
      description: 'CARREFOUR HYPERMARKET',
      amount: 45.5,
      direction: 'debit',
      currency: 'OMR',
      balance: 1754.5,
      category: 'GROCERIES',
    },
    {
      date: '2024-03-03',
      description: 'MUSCAT ELECTRICITY CO',
      amount: 25.0,
      direction: 'debit',
      currency: 'OMR',
      balance: 1729.5,
      category: 'UTILITIES',
    },
    {
      date: '2024-03-03',
      description: 'UNKNOWN NARRATIVE 999',
      amount: 15.0,
      direction: 'debit',
      currency: 'OMR',
      balance: 1714.5,
      category: 'OTHER',
      _needsReview: true,
    },
  ]

  const mockValidation: BalanceValidationResult = {
    opening_balance: 1000.0,
    closing_balance: 1714.5,
    calculated_closing_balance: 1714.5,
    total_debits: 85.5,
    total_credits: 800.0,
    net_change: 714.5,
    discrepancy_count: 0,
    reconciled: true,
    discrepancies: [],
    warnings: [],
  }

  it('calculates total credits, debits, and net flow correctly', () => {
    const summary = calculateFinancialSummary(sampleTransactions, mockValidation)
    expect(summary.totalCredits).toBe(800.0)
    expect(summary.totalDebits).toBe(85.5) // 45.5 + 25.0 + 15.0
    expect(summary.netFlow).toBe(714.5)
    expect(summary.creditCount).toBe(1)
    expect(summary.debitCount).toBe(3)
    expect(summary.transactionCount).toBe(4)
    expect(summary.isReconciled).toBe(true)
    expect(summary.needsReviewCount).toBe(1)
  })

  it('detects reconciliation mismatch when calculated closing differs from statement closing', () => {
    const brokenValidation: BalanceValidationResult = {
      opening_balance: 1000.0,
      closing_balance: 1999.0, // Mismatched statement closing
      calculated_closing_balance: 1714.5,
      total_debits: 85.5,
      total_credits: 800.0,
      net_change: 714.5,
      discrepancy_count: 1,
      reconciled: false,
      discrepancies: [{ error: 'Closing balance mismatch' }],
      warnings: ['Mismatch detected'],
    }
    const summary = calculateFinancialSummary(sampleTransactions, brokenValidation)
    expect(summary.isReconciled).toBe(false)
    expect(summary.discrepancyCount).toBe(1)
  })

  it('calculates category breakdown percentages summing properly', () => {
    const breakdown = calculateCategoryBreakdown(sampleTransactions)
    expect(breakdown.length).toBe(4)
    const totalAmount = breakdown.reduce((sum, item) => sum + item.total, 0)
    expect(totalAmount).toBe(885.5) // 800 + 45.5 + 25 + 15

    const salary = breakdown.find((b) => b.category === 'SALARY')
    expect(salary).toBeDefined()
    expect(salary?.total).toBe(800.0)
    expect(salary?.count).toBe(1)
  })

  it('handles empty transactions gracefully in category breakdown', () => {
    const breakdown = calculateCategoryBreakdown([])
    expect(breakdown).toEqual([])
  })

  it('calculates daily cash flow sorted chronologically', () => {
    const daily = calculateDailyCashFlow(sampleTransactions)
    expect(daily.length).toBe(3)
    expect(daily[0].date).toBe('2024-03-01')
    expect(daily[0].credits).toBe(800.0)
    expect(daily[0].debits).toBe(0)

    expect(daily[2].date).toBe('2024-03-03')
    expect(daily[2].debits).toBe(40.0) // 25 + 15
  })

  it('ranks top outflow merchants by debit amount descending', () => {
    const topMerchants = calculateTopOutflowMerchants(sampleTransactions, 3)
    expect(topMerchants.length).toBe(3)
    expect(topMerchants[0].name).toContain('CARREFOUR')
    expect(topMerchants[0].amount).toBe(45.5)
    expect(topMerchants[1].name).toContain('MUSCAT ELECTRICITY')
    expect(topMerchants[1].amount).toBe(25.0)
  })
})
