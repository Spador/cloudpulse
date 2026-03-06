import { useQuery } from '@tanstack/react-query'
import { apiFetch } from '../api/client'
import type { CostsResponse } from '../types'
import mockCosts from '../mock/costs.json'

export function useCosts(days: number, mock: boolean) {
  return useQuery<CostsResponse>({
    queryKey: ['costs', days, mock],
    queryFn: async () => {
      if (mock) return mockCosts as CostsResponse
      return apiFetch<CostsResponse>('/api/costs', { days: String(days) })
    },
    staleTime: 5 * 60 * 1000,
  })
}
