import { createApiClient, normalizeApiError } from './client'
import { ExtractionResponse } from '../types'

export interface ExtractOptions {
  profile?: string
  outputFormat?: 'json' | 'csv' | 'benchmark'
  useMl?: boolean
  useTransformers?: boolean
  onUploadProgress?: (progressPercent: number) => void
}

export async function extractStatement(
  file: File | Blob,
  options?: ExtractOptions
): Promise<ExtractionResponse> {
  const client = createApiClient()
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('profile', options?.profile || 'auto')
    formData.append('output_format', options?.outputFormat || 'json')
    formData.append('use_ml', options?.useMl !== false ? 'true' : 'false')
    formData.append('use_transformers', options?.useTransformers ? 'true' : 'false')

    // Do NOT manually override Content-Type header so Axios generates the exact boundary string
    const res = await client.post<ExtractionResponse>('/extract', formData, {
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          options?.onUploadProgress?.(percent)
        }
      },
    })
    return res.data
  } catch (err) {
    throw normalizeApiError(err, 'POST /extract')
  }
}
