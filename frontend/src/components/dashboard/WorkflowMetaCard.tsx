import type { OcrExtractionResult } from '../../types/ocr'

interface WorkflowMetaCardProps {
  executionMode: 'sync' | 'queued'
  ocr: OcrExtractionResult | null
  generatedAt: string
}

export const WorkflowMetaCard = ({ executionMode, ocr, generatedAt }: WorkflowMetaCardProps) => {
  return (
    <div className="glass-card">
      <p className="section-title">Workflow Metadata</p>
      <div className="mt-3 space-y-2 text-sm text-slate-600">
        <p>
          <span className="font-semibold text-slate-800">Mode:</span>{' '}
          {executionMode === 'queued' ? 'Queued workers (Celery)' : 'Synchronous API'}
        </p>
        <p>
          <span className="font-semibold text-slate-800">Generated:</span>{' '}
          {new Date(generatedAt).toLocaleString()}
        </p>
        {ocr ? (
          <>
            <p>
              <span className="font-semibold text-slate-800">OCR Match:</span> {ocr.matched_drug}
            </p>
            <p>
              <span className="font-semibold text-slate-800">OCR Confidence:</span>{' '}
              {(ocr.confidence_score * 100).toFixed(1)}%
            </p>
          </>
        ) : (
          <p className="rounded-md border border-slate-200 bg-slate-50 p-2 text-xs text-slate-500">
            No OCR run recorded in this workflow.
          </p>
        )}
      </div>
    </div>
  )
}
