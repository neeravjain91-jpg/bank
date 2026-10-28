import { createApiClient, normalizeApiError } from './client'
import { HealthResponse } from '../types'

export async function fetchHealth(): Promise<HealthResponse> {
  const client = createApiClient()
  try {
    const res = await client.get<HealthResponse>('/health')
    return res.data
  } catch (err) {
    throw normalizeApiError(err, 'GET /health')
  }
}
