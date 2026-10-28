/**
 * Banking currency formatting utilities.
 * Full precision support for 3-decimal currencies (OMR, BHD, KWD)
 * and 2-decimal currencies (USD, EUR, SGD, HKD, CAD).
 */

export function getCurrencyDecimals(currency: string = 'OMR'): number {
  const c = currency.toUpperCase().trim()
  if (['OMR', 'BHD', 'KWD', 'JOD'].includes(c)) return 3
  if (['JPY', 'KRW', 'VND'].includes(c)) return 0
  return 2
}

export function formatCurrency(
  amount: number | null | undefined,
  currency: string = 'OMR',
  options?: { showSymbol?: boolean; customDecimals?: number }
): string {
  if (amount === null || amount === undefined || isNaN(amount)) {
    return '—'
  }

  const curr = (currency || 'OMR').toUpperCase().trim()
  const decimals = options?.customDecimals ?? getCurrencyDecimals(curr)

  const formatted = new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(Math.abs(amount))

  const sign = amount < 0 ? '-' : ''
  if (options?.showSymbol === false) {
    return `${sign}${formatted}`
  }
  return `${sign}${formatted} ${curr}`
}

export function formatAmountOnly(
  amount: number | null | undefined,
  currency: string = 'OMR'
): string {
  if (amount === null || amount === undefined || isNaN(amount)) return '—'
  const decimals = getCurrencyDecimals(currency)
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(amount)
}

export interface CategoryStyle {
  bg: string
  text: string
  chartColor: string
  label: string
  border?: string
}

export const CATEGORY_STYLES: Record<string, CategoryStyle> = {
  Income: {
    bg: '#DDF3E8',
    text: '#0B6B43',
    chartColor: '#10B981',
    label: 'Income',
  },
  INCOME: {
    bg: '#DDF3E8',
    text: '#0B6B43',
    chartColor: '#10B981',
    label: 'Income',
  },
  INCOME_SALARY: {
    bg: '#DDF3E8',
    text: '#0B6B43',
    chartColor: '#10B981',
    label: 'Income',
  },
  Groceries: {
    bg: '#E3EEFB',
    text: '#1F4E8C',
    chartColor: '#2F6FD0',
    label: 'Groceries',
  },
  GROCERIES: {
    bg: '#E3EEFB',
    text: '#1F4E8C',
    chartColor: '#2F6FD0',
    label: 'Groceries',
  },
  MERCHANT_POS: {
    bg: '#E3EEFB',
    text: '#1F4E8C',
    chartColor: '#2F6FD0',
    label: 'Groceries / Retail',
  },
  Utilities: {
    bg: '#FFF1D6',
    text: '#7A4A00',
    chartColor: '#E0A100',
    label: 'Utilities',
  },
  UTILITIES: {
    bg: '#FFF1D6',
    text: '#7A4A00',
    chartColor: '#E0A100',
    label: 'Utilities',
  },
  UTILITIES_SERVICES: {
    bg: '#FFF1D6',
    text: '#7A4A00',
    chartColor: '#E0A100',
    label: 'Utilities',
  },
  Transport: {
    bg: '#E8E4FA',
    text: '#4B3A9A',
    chartColor: '#8E6CE0',
    label: 'Transport',
  },
  TRANSPORT: {
    bg: '#E8E4FA',
    text: '#4B3A9A',
    chartColor: '#8E6CE0',
    label: 'Transport',
  },
  Cash: {
    bg: '#EDEFF2',
    text: '#3B4656',
    chartColor: '#3B4656',
    label: 'Cash',
  },
  CASH: {
    bg: '#EDEFF2',
    text: '#3B4656',
    chartColor: '#3B4656',
    label: 'Cash',
  },
  ATM_CASH: {
    bg: '#EDEFF2',
    text: '#3B4656',
    chartColor: '#3B4656',
    label: 'Cash',
  },
  Transfers: {
    bg: '#D9F1F3',
    text: '#0B6169',
    chartColor: '#0E7C86',
    label: 'Transfers',
  },
  TRANSFERS: {
    bg: '#D9F1F3',
    text: '#0B6169',
    chartColor: '#0E7C86',
    label: 'Transfers',
  },
  TRANSFER_P2P: {
    bg: '#D9F1F3',
    text: '#0B6169',
    chartColor: '#0E7C86',
    label: 'Transfers',
  },
  Dining: {
    bg: '#FBE3EC',
    text: '#9B1C4B',
    chartColor: '#D6336C',
    label: 'Dining',
  },
  DINING: {
    bg: '#FBE3EC',
    text: '#9B1C4B',
    chartColor: '#D6336C',
    label: 'Dining',
  },
  BANK_FEES: {
    bg: '#FBE3EC',
    text: '#9B1C4B',
    chartColor: '#D6336C',
    label: 'Bank Fees',
  },
  INVESTMENT_DIVIDEND: {
    bg: '#DDF3E8',
    text: '#0B6B43',
    chartColor: '#10B981',
    label: 'Investments',
  },
  OTHER: {
    bg: '#EDEFF2',
    text: '#55657A',
    chartColor: '#8A99AD',
    label: 'Other',
  },
}

export function getCategoryStyle(category?: string | null): CategoryStyle {
  if (!category) {
    return {
      bg: '#EDEFF2',
      text: '#55657A',
      chartColor: '#8A99AD',
      label: 'Other',
    }
  }

  // Exact match
  if (CATEGORY_STYLES[category]) {
    return CATEGORY_STYLES[category]
  }

  // Case-insensitive or normalized match
  const upper = category.toUpperCase().replace(/\s+/g, '_')
  if (CATEGORY_STYLES[upper]) {
    return CATEGORY_STYLES[upper]
  }

  if (upper.includes('SALARY') || upper.includes('INCOME')) return CATEGORY_STYLES.Income
  if (upper.includes('GROCER') || upper.includes('FOOD') || upper.includes('STORE')) return CATEGORY_STYLES.Groceries
  if (upper.includes('UTIL') || upper.includes('BILL') || upper.includes('ELECTRIC') || upper.includes('PHONE')) return CATEGORY_STYLES.Utilities
  if (upper.includes('TRANS') && upper.includes('PORT') || upper.includes('FUEL') || upper.includes('SHELL') || upper.includes('PETROL')) return CATEGORY_STYLES.Transport
  if (upper.includes('ATM') || upper.includes('CASH')) return CATEGORY_STYLES.Cash
  if (upper.includes('TRANSFER') || upper.includes('P2P')) return CATEGORY_STYLES.Transfers
  if (upper.includes('DINING') || upper.includes('RESTAURANT') || upper.includes('TALABAT')) return CATEGORY_STYLES.Dining

  return {
    bg: '#EDEFF2',
    text: '#55657A',
    chartColor: '#8A99AD',
    label: category,
  }
}

// Retain legacy export for backwards compatibility with tests
export const CATEGORY_COLORS = CATEGORY_STYLES
