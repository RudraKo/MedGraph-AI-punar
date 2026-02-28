import { AnimatePresence, motion } from 'framer-motion'
import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { ErrorState } from '../components/common/ErrorState'
import { LoadingState } from '../components/common/LoadingState'
import { MedicationComposer } from '../components/common/MedicationComposer'
import { PageHeader } from '../components/common/PageHeader'
import { PipelineModeSwitch } from '../components/common/PipelineModeSwitch'
import { useInteractionAnalysis } from '../hooks/useInteractionAnalysis'
import { useOcrExtraction } from '../hooks/useOcrExtraction'
import { useQueuedWorkflow } from '../hooks/useQueuedWorkflow'
import { useScheduleOptimization } from '../hooks/useScheduleOptimization'
import type { MedicationDosageInput } from '../types/schedule'
import type { DashboardWorkflowState } from '../types/workflow'
import { saveWorkflow } from '../utils/storage'

const dropzoneMotion = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0 },
}

const normalizeDrugName = (name: string) => name.trim().toUpperCase()

const upsertDosage = (
  dosages: MedicationDosageInput[],
  candidate: MedicationDosageInput,
): MedicationDosageInput[] => {
  const normalizedName = normalizeDrugName(candidate.drug_name)
  if (!normalizedName) return dosages

  const normalizedFrequency = Math.max(1, Math.floor(candidate.frequency || 1))

  const existing = dosages.find((item) => item.drug_name === normalizedName)
  if (existing) {
    return dosages.map((item) =>
      item.drug_name === normalizedName
        ? { ...item, frequency: Math.max(item.frequency, normalizedFrequency) }
        : item,
    )
  }

  return [...dosages, { drug_name: normalizedName, frequency: normalizedFrequency }]
}

const formatFileSize = (sizeInBytes: number) => {
  if (sizeInBytes < 1024) return `${sizeInBytes} B`
  if (sizeInBytes < 1024 * 1024) return `${(sizeInBytes / 1024).toFixed(1)} KB`
  return `${(sizeInBytes / (1024 * 1024)).toFixed(2)} MB`
}

export const PrescriptionUploadPage = () => {
  const navigate = useNavigate()

  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [globalError, setGlobalError] = useState<string | null>(null)
  const [executionMode, setExecutionMode] = useState<'sync' | 'queued'>('sync')
  const [workflowStage, setWorkflowStage] = useState<string | null>(null)
  const [dosages, setDosages] = useState<MedicationDosageInput[]>([])

  const ocrMutation = useOcrExtraction()
  const interactionMutation = useInteractionAnalysis()
  const scheduleMutation = useScheduleOptimization()
  const queuedWorkflowMutation = useQueuedWorkflow()

  const isExtracting = ocrMutation.isPending
  const isGenerating =
    interactionMutation.isPending || scheduleMutation.isPending || queuedWorkflowMutation.isPending

  const activeError =
    globalError ??
    (ocrMutation.error as Error | null)?.message ??
    (interactionMutation.error as Error | null)?.message ??
    (scheduleMutation.error as Error | null)?.message ??
    (queuedWorkflowMutation.error as Error | null)?.message ??
    null

  const extractedDrugs = useMemo(() => dosages.map((item) => item.drug_name), [dosages])

  const onFilePicked = (file: File | null) => {
    setGlobalError(null)
    setSelectedFile(file)
    setWorkflowStage(null)
    ocrMutation.reset()
    queuedWorkflowMutation.reset()
  }

  const handleExtract = async () => {
    if (!selectedFile) {
      setGlobalError('Please upload a prescription image before extraction.')
      return
    }

    setGlobalError(null)
    setWorkflowStage('Running OCR extraction...')

    try {
      const result = await ocrMutation.mutateAsync(selectedFile)
      setDosages((previous) => upsertDosage(previous, { drug_name: result.matched_drug, frequency: 1 }))
    } finally {
      setWorkflowStage(null)
    }
  }

  const buildSyncWorkflow = async (): Promise<DashboardWorkflowState> => {
    const prescribed_drugs = dosages.map((item) => item.drug_name)

    if (prescribed_drugs.length === 0) {
      throw new Error('Add at least one medication before generating dashboard insights.')
    }

    setWorkflowStage('Computing interactions and medication schedule...')

    const [analysis, schedule] = await Promise.all([
      interactionMutation.mutateAsync({ prescribed_drugs }),
      scheduleMutation.mutateAsync({ dosages }),
    ])

    return {
      ocr: ocrMutation.data ?? null,
      extractedDrugs: prescribed_drugs,
      dosages,
      interactionAnalysis: analysis,
      schedule,
      createdAt: new Date().toISOString(),
      executionMode: 'sync',
    }
  }

  const buildQueuedWorkflow = async (): Promise<DashboardWorkflowState> => {
    if (!selectedFile && dosages.length === 0) {
      throw new Error('Queue mode requires a file upload or manually added medications.')
    }

    setWorkflowStage('Submitting workflow to async workers and polling job status...')

    const result = await queuedWorkflowMutation.mutateAsync({
      file: selectedFile,
      dosages,
    })

    setDosages(result.dosages)

    return {
      ocr: result.ocr,
      extractedDrugs: result.extractedDrugs,
      dosages: result.dosages,
      interactionAnalysis: result.interactionAnalysis,
      schedule: result.schedule,
      createdAt: new Date().toISOString(),
      executionMode: 'queued',
    }
  }

  const handleGenerateClinicalInsights = async () => {
    setGlobalError(null)

    try {
      const workflowPayload =
        executionMode === 'queued' ? await buildQueuedWorkflow() : await buildSyncWorkflow()

      saveWorkflow(workflowPayload)
      navigate('/dashboard', { state: workflowPayload })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to build clinical insights.'
      setGlobalError(message)
    } finally {
      setWorkflowStage(null)
    }
  }

  return (
    <section>
      <PageHeader
        eyebrow="Prescription Intelligence"
        title="From Prescription Image to Actionable Safety Graph"
        subtitle="Upload a medication label, refine extracted drugs, and generate conflict-aware safety analytics using either low-latency API mode or queued worker mode."
      />

      <motion.div
        variants={dropzoneMotion}
        initial="hidden"
        animate="show"
        className="grid gap-5 lg:grid-cols-[1.35fr_1fr]"
      >
        <div className="bg-surface-light border border-surface-border rounded-xl p-8 shadow-card flex flex-col">
          <div
            onDragOver={(event) => {
              event.preventDefault()
              setIsDragging(true)
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={(event) => {
              event.preventDefault()
              setIsDragging(false)
              const file = event.dataTransfer.files?.[0] ?? null
              onFilePicked(file)
            }}
            className={`relative group p-12 rounded-xl border-2 border-dashed transition-all duration-300 ease-out flex flex-col items-center justify-center ${isDragging ? 'border-brand-blue bg-brand-blue/5' : 'border-surface-border bg-surface-muted hover:border-brand-blue hover:bg-brand-blue/5 cursor-pointer'
              }`}
          >
            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-brand-blue/5 opacity-0 group-hover:opacity-100 transition-opacity rounded-xl pointer-events-none" />

            <svg className="h-10 w-10 text-brand-blue mb-4 group-hover:scale-110 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            <h3 className="text-lg font-semibold text-brand-navy">Upload Prescription</h3>
            <p className="mt-1 text-sm text-gray-500">Drag & drop or browse. AI will auto-extract dosages.</p>

            <div className="mt-6">
              <label className="btn-secondary cursor-pointer">
                Select File
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  className="hidden"
                  onChange={(event) => onFilePicked(event.target.files?.[0] ?? null)}
                />
              </label>
            </div>

            <AnimatePresence>
              {selectedFile ? (
                <motion.div
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="mt-4 rounded-lg border border-slate-200 bg-white/80 p-3 text-left"
                >
                  <p className="text-sm font-semibold text-slate-700">{selectedFile.name}</p>
                  <p className="text-xs text-slate-500">{formatFileSize(selectedFile.size)}</p>
                </motion.div>
              ) : null}
            </AnimatePresence>
          </div>

          <div className="mt-5">
            <p className="mb-2 text-sm font-semibold text-brand-navy">Execution Mode</p>
            <PipelineModeSwitch mode={executionMode} onChange={setExecutionMode} />
            <p className="mt-2 text-xs text-gray-500">
              {executionMode === 'queued'
                ? 'Uses /jobs endpoints and worker polling. Best for heavy OCR + graph workloads.'
                : 'Uses direct API endpoints for fastest local demo response.'}
            </p>
          </div>

          <div className="mt-8 flex flex-wrap gap-4">
            <button
              onClick={handleExtract}
              disabled={isExtracting || !selectedFile}
              className="px-6 py-2.5 rounded-lg font-bold text-sm tracking-wide transition-all duration-200 border bg-surface-muted border-surface-border text-brand-navy hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-brand-blue/30 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isExtracting ? 'Extracting...' : 'Extract Medication'}
            </button>

            <button
              onClick={handleGenerateClinicalInsights}
              disabled={isGenerating || (executionMode === 'sync' && dosages.length === 0)}
              className="px-6 py-2.5 rounded-lg font-bold text-sm tracking-wide transition-all duration-200 border bg-brand-blue border-brand-blue/90 text-white shadow-md shadow-brand-blue/20 hover:bg-brand-blue/90 focus:outline-none focus:ring-2 focus:ring-brand-blue/50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGenerating ? 'Generating Insights...' : 'Generate Risk Dashboard'}
            </button>
          </div>

          <div className="mt-6 space-y-3">
            {isExtracting ? <LoadingState label="Running OCR extraction pipeline..." /> : null}
            {isGenerating && workflowStage ? <LoadingState label={workflowStage} /> : null}
            {activeError ? <ErrorState message={activeError} /> : null}
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-surface-light border border-surface-border rounded-xl p-6 shadow-card">
            <p className="section-title">Active Medication Set</p>
            <p className="subtle-text mt-1">Prepared inputs sent to the interaction and scheduling engines.</p>

            <div className="mt-5 min-h-24 rounded-xl border border-surface-border bg-surface-muted p-4">
              {extractedDrugs.length === 0 ? (
                <p className="text-sm text-gray-500 text-center mt-6">No medications loaded yet. Extract OCR or add manually.</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {dosages.map((item) => (
                    <span
                      key={item.drug_name}
                      className="rounded-full border border-brand-blue/20 bg-brand-blue/5 px-3 py-1 text-xs font-semibold text-brand-blue"
                    >
                      {item.drug_name} · {item.frequency}/day
                    </span>
                  ))}
                </div>
              )}
            </div>

            {ocrMutation.data ? (
              <div className="mt-4 rounded-xl border border-slate-200 bg-white p-3">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">OCR Trace</p>
                <p className="mt-2 text-sm text-slate-700">Raw Text: {ocrMutation.data.extracted_text}</p>
                <p className="mt-1 text-sm text-slate-700">
                  Confidence: {(ocrMutation.data.confidence_score * 100).toFixed(1)}%
                </p>
              </div>
            ) : null}
          </div>

          <MedicationComposer dosages={dosages} onChange={setDosages} />
        </div>
      </motion.div>
    </section>
  )
}
