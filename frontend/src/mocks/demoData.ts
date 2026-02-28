import type { SeverityLevel } from '../types/api'
import type {
  AnalyzeInteractionsPayload,
  InteractionAnalysisResult,
  InteractionPair,
} from '../types/interactions'
import type { OcrExtractionResult } from '../types/ocr'
import type {
  MedicationDosageInput,
  OptimizeSchedulePayload,
  QueuedWorkflowPayload,
  ScheduleResult,
} from '../types/schedule'
import type { ReadinessStatus } from '../types/system'

const EDGE_MAP: Record<string, { severity: SeverityLevel; explanation: string }> = {
  'ASPIRIN|WARFARIN': {
    severity: 'severe',
    explanation: 'Increased bleeding risk due to additive anticoagulant effect.',
  },
  'OMEPRAZOLE|WARFARIN': {
    severity: 'moderate',
    explanation: 'Potential altered warfarin metabolism. Monitor INR closely.',
  },
  'LISINOPRIL|POTASSIUM': {
    severity: 'contraindicated',
    explanation: 'Risk of severe hyperkalemia and cardiac complications.',
  },
  'ASPIRIN|IBUPROFEN': {
    severity: 'moderate',
    explanation: 'NSAID overlap may reduce antiplatelet effectiveness and increase GI risk.',
  },
}

const severityWeight: Record<SeverityLevel, number> = {
  mild: 1,
  moderate: 2,
  severe: 4,
  contraindicated: 5,
}

const normalizeDrug = (name: string) => name.trim().toUpperCase()

const pairKey = (a: string, b: string) => [a, b].sort().join('|')

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

const bandFromScore = (score: number): string => {
  if (score < 25) return 'Low'
  if (score < 50) return 'Moderate'
  if (score < 80) return 'High'
  return 'Critical'
}

const buildInteractions = (drugs: string[]): InteractionPair[] => {
  const normalized = Array.from(new Set(drugs.map(normalizeDrug).filter(Boolean)))
  const output: InteractionPair[] = []

  for (let i = 0; i < normalized.length; i += 1) {
    for (let j = i + 1; j < normalized.length; j += 1) {
      const key = pairKey(normalized[i], normalized[j])
      const record = EDGE_MAP[key]
      if (!record) continue

      output.push({
        drug_a: normalized[i],
        drug_b: normalized[j],
        severity: record.severity,
        explanation: record.explanation,
      })
    }
  }

  return output
}

export const mockExtractDrug = async (file: File): Promise<OcrExtractionResult> => {
  await sleep(750)

  const hints = ['WARFARIN', 'ASPIRIN', 'OMEPRAZOLE', 'LISINOPRIL']
  const fileName = file.name.toUpperCase()
  const hintedDrug = hints.find((candidate) => fileName.includes(candidate)) ?? 'ASPIRIN'

  return {
    extracted_text: `${hintedDrug} 75 MG TABLET`,
    matched_drug: hintedDrug,
    confidence_score: 0.92,
  }
}

export const mockAnalyzeInteractions = async (
  payload: AnalyzeInteractionsPayload,
): Promise<InteractionAnalysisResult> => {
  await sleep(650)
  const interactions = buildInteractions(payload.prescribed_drugs)

  const severity_counts = {
    mild: interactions.filter((item) => item.severity === 'mild').length,
    moderate: interactions.filter((item) => item.severity === 'moderate').length,
    severe: interactions.filter((item) => item.severity === 'severe').length,
    contraindicated: interactions.filter((item) => item.severity === 'contraindicated').length,
  }

  const raw_weight = interactions.reduce((acc, item) => acc + severityWeight[item.severity], 0)
  const risk_score = Math.min(100, raw_weight * 14)
  const clinical_band = bandFromScore(risk_score)
  const dominant =
    (['contraindicated', 'severe', 'moderate', 'mild'] as SeverityLevel[]).find(
      (level) => severity_counts[level] > 0,
    ) ?? 'mild'

  const explanation =
    interactions.length === 0
      ? 'No known interaction edges detected for the current medication set.'
      : `Detected ${interactions.length} interaction edge(s). Dominant risk driver: ${dominant.toUpperCase()}.`

  return {
    interactions,
    risk_score,
    severity_summary: clinical_band,
    clinical_band,
    raw_weight,
    severity_counts,
    dominant_severity_driver: dominant,
    explanation,
  }
}

export const mockOptimizeSchedule = async (
  payload: OptimizeSchedulePayload,
): Promise<ScheduleResult> => {
  await sleep(600)

  const baseTimes = ['08:00', '12:00', '16:00', '20:00']
  const schedule: Array<{ time: string; medications: string[] }> = []
  let slotCursor = 0

  payload.dosages.forEach((item) => {
    for (let i = 0; i < item.frequency; i += 1) {
      const time = baseTimes[slotCursor % baseTimes.length]
      const existing = schedule.find((entry) => entry.time === time)
      if (existing) {
        existing.medications.push(normalizeDrug(item.drug_name))
      } else {
        schedule.push({ time, medications: [normalizeDrug(item.drug_name)] })
      }
      slotCursor += 1
    }
  })

  return {
    schedule,
    notes:
      'Demo mode schedule: evenly distributed doses across daytime windows. Validate with clinician before real use.',
  }
}

export const mockReadiness = async (): Promise<ReadinessStatus> => {
  await sleep(220)
  return {
    status: 'ready',
    dependencies: {
      database: true,
      cache: true,
      queue: true,
      queue_mode: 'enabled',
    },
  }
}

export const mockQueuedWorkflow = async (payload: QueuedWorkflowPayload) => {
  let dosages: MedicationDosageInput[] = payload.dosages.map((item) => ({
    drug_name: normalizeDrug(item.drug_name),
    frequency: Math.max(1, Math.floor(item.frequency || 1)),
  }))

  let ocr: OcrExtractionResult | null = null
  if (payload.file) {
    const result = await mockExtractDrug(payload.file)
    ocr = result
    const found = dosages.some((item) => item.drug_name === result.matched_drug)
    if (!found) {
      dosages = [...dosages, { drug_name: result.matched_drug, frequency: 1 }]
    }
  }

  const extractedDrugs = dosages.map((item) => item.drug_name)
  const [interactionAnalysis, schedule] = await Promise.all([
    mockAnalyzeInteractions({ prescribed_drugs: extractedDrugs }),
    mockOptimizeSchedule({ dosages }),
  ])

  return {
    ocr,
    dosages,
    extractedDrugs,
    interactionAnalysis,
    schedule,
  }
}
