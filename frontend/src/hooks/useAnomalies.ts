import { useQuery } from '@tanstack/react-query'
import { apiFetch } from '../api/client'
import type { AnomaliesResponse } from '../types'
import mockAnomalies from '../mock/anomalies.json'

export function useAnomalies(days: number, mock: boolean) {
  return useQuery<AnomaliesResponse>({
    queryKey: ['anomalies', days, mock],
    queryFn: async () => {
      if (mock) return mockAnomalies as AnomaliesResponse
      return apiFetch<AnomaliesResponse>('/api/anomalies', { days: String(days) })
    },
    staleTime: 5 * 60 * 1000,
  })
}
