import type { InteractionAnalysisResult } from '../../types/interactions'

interface KpiStripProps {
  analysis: InteractionAnalysisResult
  medicationCount: number
}

export const KpiStrip = ({ analysis, medicationCount }: KpiStripProps) => {
  const criticalEdges = analysis.interactions.filter(
    (item) => item.severity === 'severe' || item.severity === 'contraindicated',
  ).length

  const kpis = [
    { label: 'Medications', value: medicationCount, tone: 'text-clinic-700' },
    { label: 'Interactions', value: analysis.interactions.length, tone: 'text-slate-800' },
    { label: 'Critical Edges', value: criticalEdges, tone: 'text-rose-700' },
    { label: 'Raw Weight', value: analysis.raw_weight, tone: 'text-amber-700' },
  ]

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {kpis.map((kpi) => (
        <div key={kpi.label} className="glass-card p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{kpi.label}</p>
          <p className={`mt-2 text-3xl font-bold tracking-tight ${kpi.tone}`}>{kpi.value}</p>
        </div>
      ))}
    </div>
  )
}
