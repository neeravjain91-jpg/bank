import { useQuery } from '@tanstack/react-query'
import { fetchProfiles } from '../api/profiles'
import { ProfilesResponse } from '../types'
import { getApiBaseUrl } from '../api/client'

export function useProfiles() {
  const currentBaseUrl = getApiBaseUrl()

  return useQuery<ProfilesResponse, Error>({
    queryKey: ['profiles', currentBaseUrl],
    queryFn: fetchProfiles,
    staleTime: 5 * 60 * 1000,
    retry: 2,
  })
}
