import { describe, it, expect } from 'vitest'
import {
  validateStatementFile,
  validatePdfHeader,
  MAX_FILE_SIZE_BYTES,
} from '../validation'

describe('File Validation Utility Tests', () => {
  it('validates a correct PDF statement file', () => {
    const file = new File(['%PDF-1.4 dummy content'], 'statement.pdf', {
      type: 'application/pdf',
    })
    const res = validateStatementFile(file)
    expect(res.isValid).toBe(true)
    expect(res.error).toBeUndefined()
  })

  it('rejects an empty file (0 bytes)', () => {
    const emptyFile = new File([], 'empty.pdf', { type: 'application/pdf' })
    const res = validateStatementFile(emptyFile)
    expect(res.isValid).toBe(false)
    expect(res.error).toContain('empty')
  })

  it('rejects files exceeding MAX_FILE_SIZE_BYTES (20MB)', () => {
    // Mock a file larger than 20MB
    const largeFile = {
      name: 'huge_statement.pdf',
      size: MAX_FILE_SIZE_BYTES + 1024,
      type: 'application/pdf',
    } as unknown as File

    const res = validateStatementFile(largeFile)
    expect(res.isValid).toBe(false)
    expect(res.error).toContain('20MB')
  })

  it('rejects unsupported image files with helpful guidance', () => {
    const imgFile = new File(['fake image bytes'], 'statement.png', { type: 'image/png' })
    const res = validateStatementFile(imgFile)
    expect(res.isValid).toBe(false)
    expect(res.error).toContain('Image statements (.png, .jpg) are not supported')
  })

  it('rejects spreadsheet files with helpful guidance', () => {
    const csvFile = new File(['a,b,c'], 'statement.csv', { type: 'text/csv' })
    const res = validateStatementFile(csvFile)
    expect(res.isValid).toBe(false)
    expect(res.error).toContain('Spreadsheet files (.csv, .xlsx) are export formats')
  })

  it('detects valid %PDF- magic bytes header', async () => {
    const file = new File(['%PDF-1.5 some binary data'], 'test.pdf', {
      type: 'application/pdf',
    })
    const isPdf = await validatePdfHeader(file)
    expect(isPdf).toBe(true)
  })

  it('detects invalid magic bytes in disguised files', async () => {
    const fakeFile = new File(['THIS IS NOT A PDF'], 'fake.pdf', {
      type: 'application/pdf',
    })
    const isPdf = await validatePdfHeader(fakeFile)
    expect(isPdf).toBe(false)
  })
})
