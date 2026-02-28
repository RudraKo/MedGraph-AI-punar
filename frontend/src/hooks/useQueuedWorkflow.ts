import { useMutation } from '@tanstack/react-query'

import { medigraphApi } from '../api/medigraphApi'

export const useQueuedWorkflow = () =>
  useMutation({
    mutationKey: ['queued-workflow'],
    mutationFn: medigraphApi.runQueuedClinicalWorkflow,
  })
