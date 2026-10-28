import {
  Transaction,
  BalanceValidationResult,
  FinancialSummary,
  CategoryMetric,
  DailyCashFlow,
  MerchantSpending,
  Row,
} from '../types'
import { getCategoryStyle, CATEGORY_COLORS } from './currency'

export function calculateFinancialSummary(
  transactions: Transaction[],
  originalValidation?: BalanceValidationResult
): FinancialSummary {
  let totalDebits = 0
  let totalCredits = 0
  let debitCount = 0
  let creditCount = 0
  let needsReviewCount = 0
  let isModifiedAfterExtraction = false

  transactions.forEach((tx) => {
    const amt = typeof tx.amount === 'number' && !isNaN(tx.amount) ? Math.abs(tx.amount) : 0
    if (tx.direction === 'debit') {
      totalDebits += amt
      debitCount += 1
    } else {
      totalCredits += amt
      creditCount += 1
    }

    if (
      tx._needsReview ||
      tx._isNew ||
      (tx._categoryConfidence !== null &&
        tx._categoryConfidence !== undefined &&
        tx._categoryConfidence < 0.6)
    ) {
      needsReviewCount += 1
    }

    if (tx._isEdited || tx._isNew) {
      isModifiedAfterExtraction = true
    }
  })

  totalDebits = Math.round(totalDebits * 1000) / 1000
  totalCredits = Math.round(totalCredits * 1000) / 1000
  const netFlow = Math.round((totalCredits - totalDebits) * 1000) / 1000

  const openingBalance = originalValidation?.opening_balance ?? null
  const closingBalance = originalValidation?.closing_balance ?? null

  const calculatedClosingBalance =
    openingBalance !== null
      ? Math.round((openingBalance + totalCredits - totalDebits) * 1000) / 1000
      : null

  const isReconciled =
    closingBalance !== null && calculatedClosingBalance !== null
      ? Math.abs(closingBalance - calculatedClosingBalance) < 0.005
      : originalValidation?.reconciled ?? true

  return {
    totalCredits,
    totalDebits,
    netFlow,
    openingBalance,
    closingBalance,
    calculatedClosingBalance,
    transactionCount: transactions.length,
    creditCount,
    debitCount,
    isReconciled,
    isModifiedAfterExtraction,
    discrepancyCount: isReconciled ? 0 : 1,
    needsReviewCount,
  }
}

export interface RowSummaryMetrics {
  totalCredits: number
  creditCount: number
  totalDebits: number
  debitCount: number
  netFlow: number
  openingBalance: number
  closingBalance: number
  needsReviewCount: number
}

export function calculateRowSummary(
  rows: Row[],
  defaultOpening: number = 1562.45
): RowSummaryMetrics {
  let totalCredits = 0
  let creditCount = 0
  let totalDebits = 0
  let debitCount = 0
  let needsReviewCount = 0

  rows.forEach((r) => {
    if (r.credit !== null && !isNaN(r.credit) && r.credit > 0) {
      totalCredits += r.credit
      creditCount += 1
    }
    if (r.debit !== null && !isNaN(r.debit) && r.debit > 0) {
      totalDebits += r.debit
      debitCount += 1
    }
    if (r.needsReview) {
      needsReviewCount += 1
    }
  })

  totalCredits = Math.round(totalCredits * 1000) / 1000
  totalDebits = Math.round(totalDebits * 1000) / 1000
  const netFlow = Math.round((totalCredits - totalDebits) * 1000) / 1000

  // Calculate opening and closing balance
  const openingBalance = Math.round(defaultOpening * 1000) / 1000
  const closingBalance = Math.round((openingBalance + netFlow) * 1000) / 1000

  return {
    totalCredits,
    creditCount,
    totalDebits,
    debitCount,
    netFlow,
    openingBalance,
    closingBalance,
    needsReviewCount,
  }
}

export interface CategorySpendingItem {
  name: string
  amount: number
  percent: number
  color: string
}

export function calculateSpendingByCategory(rows: Row[]): {
  totalSpent: number
  items: CategorySpendingItem[]
} {
  const map: Record<string, number> = {}
  let totalSpent = 0

  rows.forEach((r) => {
    if (r.debit !== null && !isNaN(r.debit) && r.debit > 0) {
      const cat = r.category || 'Other'
      map[cat] = (map[cat] || 0) + r.debit
      totalSpent += r.debit
    }
  })

  totalSpent = Math.round(totalSpent * 1000) / 1000

  const items: CategorySpendingItem[] = Object.entries(map)
    .map(([cat, amt]) => {
      const rounded = Math.round(amt * 1000) / 1000
      const percent = totalSpent > 0 ? Math.round((rounded / totalSpent) * 1000) / 10 : 0
      const style = getCategoryStyle(cat)
      return {
        name: style.label || cat,
        amount: rounded,
        percent,
        color: style.chartColor,
      }
    })
    .sort((a, b) => b.amount - a.amount)

  return { totalSpent, items }
}

export interface BalancePoint {
  date: string
  balance: number
  rawDate: string
}

export function calculateBalanceHistory(
  rows: Row[],
  openingBalance: number = 1562.45
): BalancePoint[] {
  let currentBalance = openingBalance
  const points: BalancePoint[] = []

  rows.forEach((r) => {
    if (r.balance !== null && r.balance !== undefined && !isNaN(r.balance)) {
      currentBalance = r.balance
    } else {
      if (r.credit) currentBalance += r.credit
      if (r.debit) currentBalance -= r.debit
    }

    points.push({
      date: r.date,
      balance: Math.round(currentBalance * 1000) / 1000,
      rawDate: r.date,
    })
  })

  return points
}

export function calculateCategoryBreakdown(transactions: Transaction[]): CategoryMetric[] {
  const map: Record<string, { total: number; count: number }> = {}
  let grandTotal = 0

  transactions.forEach((tx) => {
    const amt = typeof tx.amount === 'number' ? Math.abs(tx.amount) : 0
    const cat = tx.category || 'OTHER'
    if (!map[cat]) {
      map[cat] = { total: 0, count: 0 }
    }
    map[cat].total += amt
    map[cat].count += 1
    grandTotal += amt
  })

  return Object.entries(map)
    .map(([cat, val]) => {
      const total = Math.round(val.total * 1000) / 1000
      return {
        category: cat,
        label: CATEGORY_COLORS[cat]?.label || cat,
        total,
        count: val.count,
        percentage: grandTotal > 0 ? Math.round((total / grandTotal) * 100) : 0,
      }
    })
    .sort((a, b) => b.total - a.total)
}

export function calculateDailyCashFlow(transactions: Transaction[]): DailyCashFlow[] {
  const map: Record<string, { debits: number; credits: number }> = {}

  transactions.forEach((tx) => {
    if (!tx.date) return
    const amt = typeof tx.amount === 'number' ? Math.abs(tx.amount) : 0
    if (!map[tx.date]) {
      map[tx.date] = { debits: 0, credits: 0 }
    }
    if (tx.direction === 'debit') {
      map[tx.date].debits += amt
    } else {
      map[tx.date].credits += amt
    }
  })

  return Object.entries(map)
    .sort((a, b) => new Date(a[0]).getTime() - new Date(b[0]).getTime())
    .map(([date, val]) => ({
      date,
      debits: Math.round(val.debits * 1000) / 1000,
      credits: Math.round(val.credits * 1000) / 1000,
      net: Math.round((val.credits - val.debits) * 1000) / 1000,
    }))
}

export function calculateTopOutflowMerchants(
  transactions: Transaction[],
  limit = 5
): MerchantSpending[] {
  const map: Record<string, { amount: number; count: number }> = {}
  let totalDebits = 0

  transactions
    .filter((tx) => tx.direction === 'debit')
    .forEach((tx) => {
      const amt = typeof tx.amount === 'number' ? Math.abs(tx.amount) : 0
      const desc = (tx.description || 'UNKNOWN').slice(0, 34).trim()
      if (!map[desc]) {
        map[desc] = { amount: 0, count: 0 }
      }
      map[desc].amount += amt
      map[desc].count += 1
      totalDebits += amt
    })

  return Object.entries(map)
    .sort((a, b) => b[1].amount - a[1].amount)
    .slice(0, limit)
    .map(([name, val]) => ({
      name,
      amount: Math.round(val.amount * 1000) / 1000,
      count: val.count,
      percentage: totalDebits > 0 ? Math.round((val.amount / totalDebits) * 100) : 0,
    }))
}
