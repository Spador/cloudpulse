import { useQuery } from '@tanstack/react-query'
import { apiFetch } from '../api/client'
import type { ResourcesResponse } from '../types'
import mockResources from '../mock/resources.json'

export function useResources(mock: boolean) {
  return useQuery<ResourcesResponse>({
    queryKey: ['resources', mock],
    queryFn: async () => {
      if (mock) return mockResources as ResourcesResponse
      return apiFetch<ResourcesResponse>('/api/resources')
    },
    staleTime: 5 * 60 * 1000,
  })
}
