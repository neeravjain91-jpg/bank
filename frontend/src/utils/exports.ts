import * as XLSX from 'xlsx'
import { Transaction, ExtractionResponse, FinancialSummary, Row } from '../types'

/**
 * Escapes text for RFC 4180 CSV compliance.
 */
function escapeCsvCell(value: unknown): string {
  if (value === null || value === undefined) return ''
  const str = String(value)
  if (str.includes(',') || str.includes('"') || str.includes('\n') || str.includes('\r')) {
    return `"${str.replace(/"/g, '""')}"`
  }
  return str
}

export function generateCsvContent(transactions: Transaction[]): string {
  const headers = [
    'Date',
    'Value_Date',
    'Description',
    'Direction',
    'Debit',
    'Credit',
    'Amount',
    'Currency',
    'Balance',
    'Category',
    'Channel',
    'Reference_ID',
    'Account_ID',
  ]

  const rows = transactions.map((t) => [
    escapeCsvCell(t.date),
    escapeCsvCell(t.value_date || ''),
    escapeCsvCell(t.description),
    escapeCsvCell(t.direction),
    escapeCsvCell(t.direction === 'debit' ? t.amount : ''),
    escapeCsvCell(t.direction === 'credit' ? t.amount : ''),
    escapeCsvCell(t.amount),
    escapeCsvCell(t.currency || ''),
    escapeCsvCell(t.balance ?? ''),
    escapeCsvCell(t.category || ''),
    escapeCsvCell(t.channel || ''),
    escapeCsvCell(t.reference_id || ''),
    escapeCsvCell(t.account_id || ''),
  ])

  return [headers.join(','), ...rows.map((r) => r.join(','))].join('\r\n')
}

export function exportToCsv(
  transactions: Transaction[],
  fileName = 'extracted_transactions.csv'
): void {
  const csvContent = generateCsvContent(transactions)
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  downloadBlob(blob, fileName)
}

export function exportRowsToCsv(
  rows: Row[],
  fileName = 'extracted_transactions.csv'
): void {
  const headers = ['Date', 'Description', 'Debit', 'Credit', 'Balance', 'Category', 'Needs_Review']
  const dataRows = rows.map((r) => [
    escapeCsvCell(r.date),
    escapeCsvCell(r.description),
    escapeCsvCell(r.debit ?? ''),
    escapeCsvCell(r.credit ?? ''),
    escapeCsvCell(r.balance ?? ''),
    escapeCsvCell(r.category || ''),
    escapeCsvCell(r.needsReview ? 'YES' : 'NO'),
  ])

  const csvContent = [headers.join(','), ...dataRows.map((r) => r.join(','))].join('\r\n')
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  downloadBlob(blob, fileName)
}

export function createExcelWorkbook(
  transactions: Transaction[],
  summary?: FinancialSummary,
  extractionData?: ExtractionResponse
): XLSX.WorkBook {
  const wb = XLSX.utils.book_new()

  // Sheet 1: Transactions
  const txRows = transactions.map((t) => ({
    'Transaction Date': t.date,
    'Value Date': t.value_date || '',
    'Description / Narrative': t.description,
    Direction: t.direction.toUpperCase(),
    'Debit (-)': t.direction === 'debit' ? t.amount : '',
    'Credit (+)': t.direction === 'credit' ? t.amount : '',
    Amount: t.amount,
    Currency: t.currency || extractionData?.metadata.currency || 'OMR',
    'Running Balance': t.balance ?? '',
    'NLP Category': t.category || 'Uncategorized',
    Channel: t.channel || '',
    'Reference ID': t.reference_id || '',
    'Account ID': t.account_id || '',
  }))

  const wsTx = XLSX.utils.json_to_sheet(txRows)
  wsTx['!cols'] = [
    { wch: 14 },
    { wch: 14 },
    { wch: 45 },
    { wch: 12 },
    { wch: 12 },
    { wch: 12 },
    { wch: 12 },
    { wch: 10 },
    { wch: 14 },
    { wch: 22 },
    { wch: 16 },
    { wch: 18 },
    { wch: 12 },
  ]
  XLSX.utils.book_append_sheet(wb, wsTx, 'Transactions')

  // Sheet 2: Statement Summary & Reconciliation
  const summaryData = [
    { Field: 'Issuing Institution', Value: extractionData?.metadata.bank || 'Bank Statement' },
    { Field: 'Source File', Value: extractionData?.metadata.file_name || 'statement.pdf' },
    { Field: 'Profile Architecture', Value: extractionData?.metadata.profile_used || 'auto' },
    { Field: 'Currency', Value: extractionData?.metadata.currency || 'OMR' },
    { Field: 'Total Transactions', Value: transactions.length },
    { Field: 'Total Deposits (Credits)', Value: summary?.totalCredits ?? 0 },
    { Field: 'Total Withdrawals (Debits)', Value: summary?.totalDebits ?? 0 },
    { Field: 'Net Cash Flow', Value: summary?.netFlow ?? 0 },
    { Field: 'Opening Balance', Value: summary?.openingBalance ?? 'N/A' },
    { Field: 'Closing Balance', Value: summary?.closingBalance ?? 'N/A' },
    { Field: 'Calculated Closing Balance', Value: summary?.calculatedClosingBalance ?? 'N/A' },
    {
      Field: 'Reconciliation Status',
      Value: summary?.isReconciled ? 'RECONCILED (100% Exact Match)' : 'DISCREPANCY DETECTED',
    },
    {
      Field: 'Client Modification State',
      Value: summary?.isModifiedAfterExtraction
        ? 'MODIFIED LOCALLY BY USER'
        : 'ORIGINAL EXTRACTED STATE',
    },
  ]

  const wsSummary = XLSX.utils.json_to_sheet(summaryData)
  wsSummary['!cols'] = [{ wch: 28 }, { wch: 35 }]
  XLSX.utils.book_append_sheet(wb, wsSummary, 'Reconciliation Summary')

  return wb
}

export function exportToExcel(
  transactions: Transaction[],
  summary?: FinancialSummary,
  extractionData?: ExtractionResponse,
  fileName = 'bank_statement_analytics.xlsx'
): void {
  const wb = createExcelWorkbook(transactions, summary, extractionData)
  XLSX.writeFile(wb, fileName)
}

export function exportRowsToExcel(
  rows: Row[],
  fileName = 'bank_statement_transactions.xlsx'
): void {
  const wb = XLSX.utils.book_new()
  const txRows = rows.map((r) => ({
    Date: r.date,
    Description: r.description,
    'Debit (-)': r.debit ?? '',
    'Credit (+)': r.credit ?? '',
    Balance: r.balance ?? '',
    Category: r.category || 'Other',
    'Review Required': r.needsReview ? 'YES' : 'NO',
  }))

  const ws = XLSX.utils.json_to_sheet(txRows)
  ws['!cols'] = [
    { wch: 14 },
    { wch: 38 },
    { wch: 14 },
    { wch: 14 },
    { wch: 14 },
    { wch: 18 },
    { wch: 16 },
  ]
  XLSX.utils.book_append_sheet(wb, ws, 'Transactions')
  XLSX.writeFile(wb, fileName)
}

export function exportToJson(data: unknown, fileName = 'statement_extraction.json'): void {
  const jsonStr = JSON.stringify(data, null, 2)
  const blob = new Blob([jsonStr], { type: 'application/json' })
  downloadBlob(blob, fileName)
}

export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text)
      return true
    } else {
      const textarea = document.createElement('textarea')
      textarea.value = text
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      const successful = document.execCommand('copy')
      document.body.removeChild(textarea)
      return successful
    }
  } catch {
    return false
  }
}

function downloadBlob(blob: Blob, fileName: string): void {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
