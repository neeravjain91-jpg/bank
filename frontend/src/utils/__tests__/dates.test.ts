import { describe, it, expect } from 'vitest'
import { formatDate, isValidIsoDate } from '../dates'

describe('Dates Utility Tests', () => {
  it('formats standard ISO YYYY-MM-DD correctly', () => {
    const formatted = formatDate('2024-03-15')
    expect(formatted).toBe('15 Mar 2024')
  })

  it('formats DD/MM/YYYY slash format correctly', () => {
    const formatted = formatDate('15/03/2024')
    expect(formatted).toBe('15 Mar 2024')
  })

  it('formats DD-MM-YYYY dash format correctly', () => {
    const formatted = formatDate('15-03-2024')
    expect(formatted).toBe('15 Mar 2024')
  })

  it('gracefully handles malformed or unknown date formats without throwing', () => {
    expect(formatDate('invalid-date')).toBe('invalid-date')
    expect(formatDate('')).toBe('—')
    expect(formatDate(null as unknown as string)).toBe('—')
    expect(formatDate(undefined as unknown as string)).toBe('—')
  })

  it('validates ISO date format with isValidIsoDate', () => {
    expect(isValidIsoDate('2024-03-15')).toBe(true)
    expect(isValidIsoDate('2024-12-31')).toBe(true)
    expect(isValidIsoDate('15/03/2024')).toBe(false)
    expect(isValidIsoDate('2024-13-01')).toBe(false) // Invalid month
    expect(isValidIsoDate('not-a-date')).toBe(false)
    expect(isValidIsoDate('')).toBe(false)
  })
})
