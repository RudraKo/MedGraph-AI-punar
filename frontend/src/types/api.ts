export interface ApiEnvelope<T> {
  success: boolean
  data: T
  error: string | null
}

export type SeverityLevel = 'mild' | 'moderate' | 'severe' | 'contraindicated'
