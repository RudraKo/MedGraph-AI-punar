import { motion } from 'framer-motion'

import type { InteractionAnalysisResult } from '../../types/interactions'
import { riskBandClass } from '../../utils/severity'

interface RiskCardProps {
  analysis: InteractionAnalysisResult
}

export const RiskCard = ({ analysis }: RiskCardProps) => {
  const badgeClass = riskBandClass(analysis.risk_score)
  const isSevere = analysis.risk_score > 7

  return (
    <motion.section
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`bg-surface-light border rounded-xl shadow-card p-6 ${isSevere ? 'border-l-4 border-l-risk-severe border-y-surface-border border-r-surface-border' : 'border-surface-border'}`}
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-gray-500 uppercase tracking-wider">Overall Risk Score</p>
          <div className="flex items-baseline mt-1">
            <span className="text-4xl font-bold tracking-tight text-brand-navy">{analysis.risk_score}</span>
            <span className="text-sm text-gray-500 ml-2">/ 100</span>
          </div>
        </div>
        <span className={`rounded-full border px-3 py-1 text-xs font-bold uppercase ${badgeClass}`}>
          {analysis.clinical_band}
        </span>
      </div>

      <p className="mt-4 text-sm text-gray-600">{analysis.explanation}</p>

      <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Metric label="Mild" value={analysis.severity_counts.mild} />
        <Metric label="Moderate" value={analysis.severity_counts.moderate} />
        <Metric label="Severe" value={analysis.severity_counts.severe} />
        <Metric label="Contra" value={analysis.severity_counts.contraindicated} />
      </div>
    </motion.section>
  )
}

interface MetricProps {
  label: string
  value: number
}

const Metric = ({ label, value }: MetricProps) => (
  <div className="rounded-xl border border-surface-border bg-surface-muted p-3 text-center transition-all hover:-translate-y-0.5 hover:shadow-sm">
    <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">{label}</p>
    <p className="mt-1 text-2xl font-bold text-brand-navy">{value}</p>
  </div>
)
