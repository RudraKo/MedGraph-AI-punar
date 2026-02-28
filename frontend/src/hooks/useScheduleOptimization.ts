import { useMutation } from '@tanstack/react-query'

import { medigraphApi } from '../api/medigraphApi'

export const useScheduleOptimization = () =>
  useMutation({
    mutationKey: ['schedule-optimization'],
    mutationFn: medigraphApi.optimizeSchedule,
  })
