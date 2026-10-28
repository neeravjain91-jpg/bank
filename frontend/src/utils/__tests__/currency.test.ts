import { describe, it, expect } from 'vitest'
import {
  formatCurrency,
  formatAmountOnly,
  getCurrencyDecimals,
  CATEGORY_COLORS,
} from '../currency'

describe('Currency Utility Tests', () => {
  it('correctly identifies OMR as 3 decimal places', () => {
    expect(getCurrencyDecimals('OMR')).toBe(3)
    expect(getCurrencyDecimals('omr')).toBe(3)
    expect(getCurrencyDecimals('KWD')).toBe(3)
    expect(getCurrencyDecimals('BHD')).toBe(3)
    expect(getCurrencyDecimals('USD')).toBe(2)
    expect(getCurrencyDecimals('EUR')).toBe(2)
    expect(getCurrencyDecimals(undefined)).toBe(3) // Default is OMR (3)
  })

  it('formats OMR amounts with 3 decimal places', () => {
    const formatted = formatCurrency(12.345, 'OMR')
    expect(formatted).toContain('12.345')
    expect(formatted).toContain('OMR')
  })

  it('formats OMR amounts with trailing zeros preserved', () => {
    const formatted = formatCurrency(100.5, 'OMR')
    expect(formatted).toContain('100.500')
  })

  it('handles negative currency values correctly', () => {
    const formatted = formatCurrency(-50.25, 'OMR')
    expect(formatted).toContain('-')
    expect(formatted).toContain('50.250')
  })

  it('handles zero values and null/undefined gracefully', () => {
    expect(formatCurrency(0, 'OMR')).toContain('0.000')
    expect(formatCurrency(null, 'OMR')).toBe('—')
    expect(formatCurrency(undefined, 'OMR')).toBe('—')
    expect(formatCurrency(NaN, 'OMR')).toBe('—')
  })

  it('formats raw amounts without currency symbol', () => {
    expect(formatAmountOnly(12.5, 'OMR')).toBe('12.500')
    expect(formatAmountOnly(250, 'USD')).toBe('250.00')
    expect(formatAmountOnly(null)).toBe('—')
  })

  it('defines valid color tokens for all standard categories', () => {
    expect(CATEGORY_COLORS.INCOME_SALARY).toBeDefined()
    expect(CATEGORY_COLORS.UTILITIES_SERVICES).toBeDefined()
    expect(CATEGORY_COLORS.MERCHANT_POS).toBeDefined()
    expect(CATEGORY_COLORS.TRANSFER_P2P).toBeDefined()
    expect(CATEGORY_COLORS.OTHER).toBeDefined()
  })
})
