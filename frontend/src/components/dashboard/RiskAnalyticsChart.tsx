import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import type { InteractionAnalysisResult } from '../../types/interactions'

interface RiskAnalyticsChartProps {
  analysis: InteractionAnalysisResult
}

// Update the severity color map for recharts using tailwind colors since we dropped original colors
const RISK_COLORS: Record<string, string> = {
  mild: '#059669', // risk-safe
  moderate: '#D97706', // risk-moderate
  severe: '#DC2626', // risk-severe
  contraindicated: '#7F1D1D', // risk-fatal
}

export const RiskAnalyticsChart = ({ analysis }: RiskAnalyticsChartProps) => {
  const chartData = [
    { name: 'Mild', value: analysis.severity_counts.mild, key: 'mild' as const },
    { name: 'Moderate', value: analysis.severity_counts.moderate, key: 'moderate' as const },
    { name: 'Severe', value: analysis.severity_counts.severe, key: 'severe' as const },
    {
      name: 'Contra',
      value: analysis.severity_counts.contraindicated,
      key: 'contraindicated' as const,
    },
  ]

  return (
    <div className="bg-surface-light border border-surface-border rounded-xl p-6 shadow-card flex flex-col h-full min-h-[350px]">
      <p className="section-title">Risk Distribution</p>
      <p className="subtle-text mt-1">Interaction severity breakdown for this regimen.</p>

      <div className="mt-8 flex-1 relative w-full">
        <div className="absolute inset-0">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
              <XAxis dataKey="name" tick={{ fill: '#4B5563', fontSize: 13, fontWeight: 600 }} axisLine={false} tickLine={false} dy={10} />
              <YAxis allowDecimals={false} tick={{ fill: '#4B5563', fontSize: 12 }} axisLine={false} tickLine={false} />
              <Tooltip
                cursor={{ fill: '#F8F9FA' }}
                contentStyle={{ borderRadius: '0.75rem', borderColor: '#E5E7EB', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)', fontWeight: 600, color: '#0F233E' }}
              />
              <Bar dataKey="value" radius={[6, 6, 0, 0]} barSize={40}>
                {chartData.map((entry) => (
                  <Cell key={entry.key} fill={RISK_COLORS[entry.key] || '#2B61B1'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
