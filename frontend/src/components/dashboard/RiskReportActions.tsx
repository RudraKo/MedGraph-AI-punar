import { useState } from 'react'
import { Link } from 'react-router-dom'

import type { DashboardWorkflowState } from '../../types/workflow'
import { exportRiskReportPdf } from '../../utils/reportPdf'

interface RiskReportActionsProps {
  workflow: DashboardWorkflowState
}

export const RiskReportActions = ({ workflow }: RiskReportActionsProps) => {
  const [toastMessage, setToastMessage] = useState<string | null>(null)

  const handleExportPdf = () => {
    const filename = exportRiskReportPdf(workflow)
    setToastMessage(`Exported ${filename}`)
    window.setTimeout(() => setToastMessage(null), 2200)
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <Link to="/" className="btn-secondary">
        New Analysis
      </Link>
      <button type="button" onClick={handleExportPdf} className="btn-primary">
        Export PDF Report
      </button>

      {toastMessage ? (
        <div className="w-full rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs font-semibold text-emerald-700 sm:w-auto">
          {toastMessage}
        </div>
      ) : null}
    </div>
  )
}
