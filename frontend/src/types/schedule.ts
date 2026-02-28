export interface MedicationDosageInput {
  drug_name: string
  frequency: number
}

export interface OptimizeSchedulePayload {
  dosages: MedicationDosageInput[]
}

export interface ScheduleSlot {
  time: string
  medications: string[]
}

export interface ScheduleResult {
  schedule: ScheduleSlot[]
  notes: string
}

export interface QueuedWorkflowPayload {
  file: File | null
  dosages: MedicationDosageInput[]
}
