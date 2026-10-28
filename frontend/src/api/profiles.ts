import { createApiClient, normalizeApiError } from './client'
import { ProfilesResponse } from '../types'

export async function fetchProfiles(): Promise<ProfilesResponse> {
  const client = createApiClient()
  try {
    const res = await client.get<ProfilesResponse>('/profiles')
    return res.data
  } catch (err) {
    throw normalizeApiError(err, 'GET /profiles')
  }
}
