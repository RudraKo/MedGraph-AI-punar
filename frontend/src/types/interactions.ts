import type { SeverityLevel } from './api'

export interface InteractionPair {
  drug_a: string
  drug_b: string
  severity: SeverityLevel
  explanation: string
}

export interface InteractionSeverityCounts {
  mild: number
  moderate: number
  severe: number
  contraindicated: number
}

export interface InteractionAnalysisResult {
  interactions: InteractionPair[]
  risk_score: number
  severity_summary: string
  clinical_band: string
  raw_weight: number
  severity_counts: InteractionSeverityCounts
  dominant_severity_driver: string
  explanation: string
}

export interface AnalyzeInteractionsPayload {
  prescribed_drugs: string[]
}
