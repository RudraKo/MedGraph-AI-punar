import type { ApiEnvelope } from '../types/api'
import type {
  AnalyzeInteractionsPayload,
  InteractionAnalysisResult,
} from '../types/interactions'
import type { JobAcceptedPayload, JobStatusPayload } from '../types/jobs'
import type { OcrExtractionResult } from '../types/ocr'
import type {
  MedicationDosageInput,
  OptimizeSchedulePayload,
  QueuedWorkflowPayload,
  ScheduleResult,
} from '../types/schedule'
import type { ReadinessStatus } from '../types/system'
import {
  mockAnalyzeInteractions,
  mockExtractDrug,
  mockOptimizeSchedule,
  mockQueuedWorkflow,
  mockReadiness,
} from '../mocks/demoData'
import { httpClient } from './httpClient'

const DEMO_MODE = (import.meta.env.VITE_DEMO_MODE ?? 'false').toLowerCase() === 'true'

const postWithFallback = async <T>(paths: string[], payload: unknown): Promise<T> => {
  let fallbackError: Error | null = null

  for (const path of paths) {
    try {
      const response = await httpClient.post<ApiEnvelope<T>>(path, payload)
      return response.data.data
    } catch (error) {
      const normalizedError = error as Error
      const message = normalizedError.message.toLowerCase()
      const isFallbackCandidate = message.includes('404') || message.includes('not found')

      if (!isFallbackCandidate) {
        throw normalizedError
      }
      fallbackError = normalizedError
    }
  }

  throw fallbackError ?? new Error('All API fallbacks failed')
}

const getUniqueNormalizedDosages = (dosages: MedicationDosageInput[]): MedicationDosageInput[] => {
  const merged = new Map<string, number>()

  dosages.forEach((item) => {
    const normalizedName = item.drug_name.trim().toUpperCase()
    if (!normalizedName) return

    const safeFrequency = Math.max(1, Math.floor(item.frequency || 1))
    merged.set(normalizedName, Math.max(safeFrequency, merged.get(normalizedName) ?? 0))
  })

  return Array.from(merged.entries()).map(([drug_name, frequency]) => ({ drug_name, frequency }))
}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

const waitForJobResult = async <T>(
  jobId: string,
  timeoutMs = 90_000,
  pollEveryMs = 1200,
): Promise<T> => {
  const startedAt = Date.now()

  while (Date.now() - startedAt < timeoutMs) {
    const statusResponse = await medigraphApi.getJobStatus<T>(jobId)

    if (statusResponse.status === 'SUCCESS') {
      if (typeof statusResponse.result === 'undefined') {
        throw new Error(`Job ${jobId} succeeded but returned no result payload.`)
      }
      return statusResponse.result
    }

    if (statusResponse.status === 'FAILURE') {
      throw new Error(statusResponse.error ?? `Job ${jobId} failed.`)
    }

    await sleep(pollEveryMs)
  }

  throw new Error(`Job ${jobId} timed out after ${Math.round(timeoutMs / 1000)} seconds.`)
}

export const medigraphApi = {
  async extractDrugFromImage(file: File): Promise<OcrExtractionResult> {
    if (DEMO_MODE) {
      return mockExtractDrug(file)
    }

    const formData = new FormData()
    formData.append('image', file)

    const response = await httpClient.post<ApiEnvelope<OcrExtractionResult>>('/ocr/extract-drug', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data.data
  },

  async analyzeInteractions(payload: AnalyzeInteractionsPayload): Promise<InteractionAnalysisResult> {
    if (DEMO_MODE) {
      return mockAnalyzeInteractions(payload)
    }

    return postWithFallback<InteractionAnalysisResult>(['/interactions/analyze', '/check-interactions'], payload)
  },

  async optimizeSchedule(payload: OptimizeSchedulePayload): Promise<ScheduleResult> {
    if (DEMO_MODE) {
      return mockOptimizeSchedule(payload)
    }

    return postWithFallback<ScheduleResult>(['/schedule/optimize', '/schedule'], payload)
  },

  async submitOcrJob(file: File): Promise<JobAcceptedPayload> {
    if (DEMO_MODE) {
      return {
        job_id: 'demo-ocr-job',
        status: 'PENDING',
        job_type: 'ocr',
      }
    }

    const formData = new FormData()
    formData.append('image', file)

    const response = await httpClient.post<ApiEnvelope<JobAcceptedPayload>>('/jobs/ocr/extract-drug', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data.data
  },

  async submitInteractionJob(payload: AnalyzeInteractionsPayload): Promise<JobAcceptedPayload> {
    if (DEMO_MODE) {
      void payload
      return {
        job_id: 'demo-interaction-job',
        status: 'PENDING',
        job_type: 'interactions',
      }
    }

    const response = await httpClient.post<ApiEnvelope<JobAcceptedPayload>>('/jobs/interactions/check', payload)
    return response.data.data
  },

  async submitScheduleJob(payload: OptimizeSchedulePayload): Promise<JobAcceptedPayload> {
    if (DEMO_MODE) {
      void payload
      return {
        job_id: 'demo-schedule-job',
        status: 'PENDING',
        job_type: 'schedule',
      }
    }

    const response = await httpClient.post<ApiEnvelope<JobAcceptedPayload>>('/jobs/schedule/generate', payload)
    return response.data.data
  },

  async getJobStatus<T>(jobId: string): Promise<JobStatusPayload<T>> {
    if (DEMO_MODE) {
      void jobId
      return {
        job_id: 'demo-job',
        status: 'SUCCESS',
        ready: true,
      }
    }

    const response = await httpClient.get<ApiEnvelope<JobStatusPayload<T>>>(`/jobs/${jobId}`)
    return response.data.data
  },

  async getReadinessStatus(): Promise<ReadinessStatus> {
    if (DEMO_MODE) {
      return mockReadiness()
    }

    const response = await httpClient.get<ReadinessStatus>('/health/ready')
    return response.data
  },

  async runQueuedClinicalWorkflow(payload: QueuedWorkflowPayload): Promise<{
    ocr: OcrExtractionResult | null
    dosages: MedicationDosageInput[]
    extractedDrugs: string[]
    interactionAnalysis: InteractionAnalysisResult
    schedule: ScheduleResult
  }> {
    if (DEMO_MODE) {
      return mockQueuedWorkflow(payload)
    }

    let ocr: OcrExtractionResult | null = null
    let dosages = getUniqueNormalizedDosages(payload.dosages)

    if (payload.file) {
      const ocrJob = await medigraphApi.submitOcrJob(payload.file)
      ocr = await waitForJobResult<OcrExtractionResult>(ocrJob.job_id)
      const extractedDrug = ocr.matched_drug

      const hasMatch = dosages.some((item) => item.drug_name === extractedDrug)
      if (!hasMatch) {
        dosages = [...dosages, { drug_name: extractedDrug, frequency: 1 }]
      }
    }

    if (dosages.length === 0) {
      throw new Error('Add at least one medication to run queued analysis.')
    }

    const prescribed_drugs = dosages.map((item) => item.drug_name)

    const [interactionJob, scheduleJob] = await Promise.all([
      medigraphApi.submitInteractionJob({ prescribed_drugs }),
      medigraphApi.submitScheduleJob({ dosages }),
    ])

    const [interactionAnalysis, schedule] = await Promise.all([
      waitForJobResult<InteractionAnalysisResult>(interactionJob.job_id),
      waitForJobResult<ScheduleResult>(scheduleJob.job_id),
    ])

    return {
      ocr,
      dosages,
      extractedDrugs: prescribed_drugs,
      interactionAnalysis,
      schedule,
    }
  },
}
