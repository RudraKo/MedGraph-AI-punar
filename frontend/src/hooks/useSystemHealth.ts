import { useQuery } from '@tanstack/react-query'

import { medigraphApi } from '../api/medigraphApi'

export const useSystemHealth = () =>
  useQuery({
    queryKey: ['system-health'],
    queryFn: medigraphApi.getReadinessStatus,
    refetchInterval: 20_000,
  })
