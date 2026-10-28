import { createApiClient, normalizeApiError } from './client'
import { CategorizeRequest, CategorizeResponse } from '../types'

export async function categorizeTransactions(
  descriptions: string[],
  useTransformers = false
): Promise<CategorizeResponse> {
  const client = createApiClient()
  try {
    const payload: CategorizeRequest = {
      descriptions,
      use_transformers: useTransformers,
    }
    const res = await client.post<CategorizeResponse>('/categorize', payload)
    return res.data
  } catch (err) {
    throw normalizeApiError(err, 'POST /categorize')
  }
}
