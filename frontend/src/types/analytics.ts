/**
 * Financial analytics models calculated from extracted transactions.
 */

export interface FinancialSummary {
  totalCredits: number
  totalDebits: number
  netFlow: number
  openingBalance: number | null
  closingBalance: number | null
  calculatedClosingBalance: number | null
  transactionCount: number
  creditCount: number
  debitCount: number
  isReconciled: boolean
  isModifiedAfterExtraction: boolean
  discrepancyCount: number
  needsReviewCount: number
}

export interface CategoryMetric {
  category: string
  label: string
  total: number
  count: number
  percentage: number
}

export interface DailyCashFlow {
  date: string
  debits: number
  credits: number
  net: number
}

export interface MerchantSpending {
  name: string
  amount: number
  count: number
  percentage: number
}

export interface HistoryItem {
  id: string
  timestamp: string
  fileName: string
  bankName: string
  currency: string
  transactionCount: number
  totalCredits: number
  totalDebits: number
  netChange: number
  reconciled: boolean
  isDemo: boolean
  data: import('./api').ExtractionResponse
  documentUrl?: string
}
