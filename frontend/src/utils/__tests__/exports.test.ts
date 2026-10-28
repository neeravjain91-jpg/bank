import { describe, it, expect } from 'vitest'
import { generateCsvContent, createExcelWorkbook } from '../exports'
import { Transaction, FinancialSummary } from '../../types'

describe('Export Utility Tests', () => {
  const transactions: Transaction[] = [
    {
      date: '2024-03-01',
      value_date: '2024-03-01',
      description: 'SALARY CREDIT, ACME "CORP"',
      direction: 'credit',
      amount: 1500.0,
      currency: 'OMR',
      balance: 2500.0,
      category: 'SALARY',
      channel: 'TRANSFER',
      reference_id: 'REF12345',
      account_id: 'ACC001',
    },
    {
      date: '2024-03-02',
      value_date: '2024-03-02',
      description: 'LULU HYPERMARKET\nOMAN',
      direction: 'debit',
      amount: 65.25,
      currency: 'OMR',
      balance: 2434.75,
      category: 'GROCERIES',
      channel: 'POS',
      reference_id: 'REF67890',
      account_id: 'ACC001',
    },
  ]

  const summary: FinancialSummary = {
    totalCredits: 1500.0,
    totalDebits: 65.25,
    netFlow: 1434.75,
    openingBalance: 1000.0,
    closingBalance: 2434.75,
    calculatedClosingBalance: 2434.75,
    transactionCount: 2,
    creditCount: 1,
    debitCount: 1,
    isReconciled: true,
    isModifiedAfterExtraction: false,
    discrepancyCount: 0,
    needsReviewCount: 0,
  }

  it('generates valid RFC 4180 CSV with escaped quotes, commas, and newlines', () => {
    const csv = generateCsvContent(transactions)
    expect(csv).toContain('Date,Value_Date,Description,Direction,Debit,Credit,Amount')
    // Check that quotes and commas are escaped
    expect(csv).toContain('"SALARY CREDIT, ACME ""CORP"""')
    // Check that newline in description is quoted
    expect(csv).toContain('"LULU HYPERMARKET\nOMAN"')
    // Check amounts
    expect(csv).toContain('1500')
    expect(csv).toContain('65.25')
  })

  it('generates Excel workbook with Transactions and Reconciliation Summary sheets', () => {
    const wb = createExcelWorkbook(transactions, summary)
    expect(wb.SheetNames).toContain('Transactions')
    expect(wb.SheetNames).toContain('Reconciliation Summary')

    const txSheet = wb.Sheets['Transactions']
    expect(txSheet).toBeDefined()

    const summarySheet = wb.Sheets['Reconciliation Summary']
    expect(summarySheet).toBeDefined()
  })
})
