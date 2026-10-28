/**
 * File validation utilities adhering strictly to the backend PDF-only pipeline.
 */

export const MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024 // 20 MB backend limit

export interface ValidationResult {
  isValid: boolean
  error?: string
}

export function validateStatementFile(file: File): ValidationResult {
  if (!file) {
    return { isValid: false, error: 'No file selected.' }
  }

  if (file.size === 0) {
    return { isValid: false, error: 'The selected file is empty (0 bytes).' }
  }

  if (file.size > MAX_FILE_SIZE_BYTES) {
    const sizeMb = (file.size / (1024 * 1024)).toFixed(1)
    return {
      isValid: false,
      error: `File size exceeds the 20MB limit (selected: ${sizeMb} MB).`,
    }
  }

  const name = file.name.toLowerCase()
  const isPdfExtension = name.endsWith('.pdf')
  const isPdfMime = file.type === 'application/pdf'

  // Explicit handling for unsupported file formats
  if (name.endsWith('.png') || name.endsWith('.jpg') || name.endsWith('.jpeg')) {
    return {
      isValid: false,
      error:
        'Image statements (.png, .jpg) are not supported by the current digital extraction pipeline. Please upload a digital native PDF statement.',
    }
  }

  if (name.endsWith('.csv') || name.endsWith('.xlsx') || name.endsWith('.xls')) {
    return {
      isValid: false,
      error:
        'Spreadsheet files (.csv, .xlsx) are export formats, not input formats. Please upload a PDF bank statement for table extraction.',
    }
  }

  if (!isPdfExtension && !isPdfMime) {
    return {
      isValid: false,
      error: 'Invalid file format. The extraction engine strictly accepts digital PDF bank statements (.pdf).',
    }
  }

  return { isValid: true }
}

/**
 * Validates the %PDF magic byte header asynchronously.
 */
export async function validatePdfHeader(file: File): Promise<boolean> {
  try {
    const slice = file.slice(0, 5)
    const buffer = await slice.arrayBuffer()
    const header = new TextDecoder('ascii').decode(buffer)
    return header.startsWith('%PDF-')
  } catch {
    return true // Fallback if browser security blocks blob slicing
  }
}
