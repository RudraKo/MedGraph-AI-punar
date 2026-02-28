import { useMutation } from '@tanstack/react-query'

import { medigraphApi } from '../api/medigraphApi'

export const useInteractionAnalysis = () =>
  useMutation({
    mutationKey: ['interaction-analysis'],
    mutationFn: medigraphApi.analyzeInteractions,
  })
