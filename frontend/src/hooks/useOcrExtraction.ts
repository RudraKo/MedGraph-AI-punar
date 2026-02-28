import { useMutation } from '@tanstack/react-query'

import { medigraphApi } from '../api/medigraphApi'

export const useOcrExtraction = () =>
  useMutation({
    mutationKey: ['ocr-extraction'],
    mutationFn: medigraphApi.extractDrugFromImage,
  })
