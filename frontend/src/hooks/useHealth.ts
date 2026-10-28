import { useQuery } from '@tanstack/react-query'
import { useState, useRef } from 'react'
import { fetchHealth } from '../api/health'
import { HealthResponse } from '../types'
import { getApiBaseUrl } from '../api/client'

export function useHealth() {
  const [latency, setLatency] = useState<number | null>(null)
  const currentBaseUrl = getApiBaseUrl()
  const startRef = useRef<number>(0)

  const query = useQuery<HealthResponse, Error>({
    queryKey: ['health', currentBaseUrl],
    queryFn: async () => {
      startRef.current = performance.now()
      const data = await fetchHealth()
      const end = performance.now()
      setLatency(Math.round(end - startRef.current))
      return data
    },
    refetchInterval: 30000, // Strict 30s polling per Phase 4.1
    retry: 1,
    refetchOnWindowFocus: true,
  })

  const isOnline = query.isSuccess && query.data?.status === 'healthy'
  const isDegraded =
    query.isSuccess &&
    (!query.data?.ml_line_classifier_loaded || !query.data?.nlp_categorizer_loaded)

  return {
    ...query,
    isOnline,
    isDegraded,
    latency,
    baseUrl: currentBaseUrl,
  }
}
