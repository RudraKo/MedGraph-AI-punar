import type { InteractionAnalysisResult } from './interactions'
import type { OcrExtractionResult } from './ocr'
import type { MedicationDosageInput, ScheduleResult } from './schedule'

export interface DashboardWorkflowState {
  ocr: OcrExtractionResult | null
  extractedDrugs: string[]
  dosages: MedicationDosageInput[]
  interactionAnalysis: InteractionAnalysisResult
  schedule: ScheduleResult
  createdAt: string
  executionMode: 'sync' | 'queued'
}
