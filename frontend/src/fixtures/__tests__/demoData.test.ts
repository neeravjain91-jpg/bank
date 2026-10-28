import { describe, it, expect } from 'vitest'
import { DEMO_BANK_MUSCAT_FIXTURE, SAMPLE_ROWS, SAMPLE_FILE_METADATA } from '../demoData'

describe('Demo Fixture Integrity Tests', () => {
  it('contains exactly 8 transactions matching Bank Muscat statement specification', () => {
    expect(SAMPLE_ROWS.length).toBe(8)
    expect(DEMO_BANK_MUSCAT_FIXTURE.transactions.length).toBe(8)
  })

  it('has exactly 2 credits and 6 debits', () => {
    const credits = SAMPLE_ROWS.filter((r) => r.credit !== null && r.credit > 0)
    const debits = SAMPLE_ROWS.filter((r) => r.debit !== null && r.debit > 0)
    expect(credits.length).toBe(2)
    expect(debits.length).toBe(6)
  })

  it('has exact credit and debit totals matching Bank Muscat validation', () => {
    const totalCredits = SAMPLE_ROWS
      .filter((r) => r.credit !== null)
      .reduce((sum, r) => sum + (r.credit ?? 0), 0)

    const totalDebits = SAMPLE_ROWS
      .filter((r) => r.debit !== null)
      .reduce((sum, r) => sum + (r.debit ?? 0), 0)

    expect(Math.round(totalCredits * 1000) / 1000).toBe(2100.0)
    expect(Math.round(totalDebits * 1000) / 1000).toBe(210.0)
    expect(Math.round((totalCredits - totalDebits) * 1000) / 1000).toBe(1890.0)
  })

  it('verifies exact mathematical reconciliation with opening and closing balances', () => {
    const opening = SAMPLE_FILE_METADATA.openingBalance
    const closing = SAMPLE_FILE_METADATA.closingBalance
    const calculated = opening + 2100.0 - 210.0
    expect(Math.round(calculated * 1000) / 1000).toBe(closing)
  })

  it('identifies exactly 1 low-confidence transaction flagged for review', () => {
    const needsReview = SAMPLE_ROWS.filter((r) => r.needsReview)
    expect(needsReview.length).toBe(1)
    expect(needsReview[0].description).toContain('Talabat')
    expect(needsReview[0].confidence).toBeLessThan(0.6)
  })
})
