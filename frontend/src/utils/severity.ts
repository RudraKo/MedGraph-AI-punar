import type { SeverityLevel } from '../types/api'

export const severityOrder: SeverityLevel[] = ['mild', 'moderate', 'severe', 'contraindicated']

export const severityColorMap: Record<SeverityLevel, string> = {
  mild: '#059669', // risk-safe
  moderate: '#D97706', // risk-moderate
  severe: '#DC2626', // risk-severe
  contraindicated: '#7F1D1D', // risk-fatal
}

export const severityBadgeClass: Record<SeverityLevel, string> = {
  mild: 'bg-risk-safe/10 text-risk-safe border-risk-safe/20',
  moderate: 'bg-risk-moderate/10 text-risk-moderate border-risk-moderate/20',
  severe: 'bg-risk-severe/10 text-risk-severe border-risk-severe/20',
  contraindicated: 'bg-risk-fatal/10 text-risk-fatal border-risk-fatal/20',
}

export const riskBandClass = (score: number): string => {
  if (score < 25) return 'bg-risk-safe/10 text-risk-safe border-risk-safe/20'
  if (score < 50) return 'bg-risk-moderate/10 text-risk-moderate border-risk-moderate/20'
  if (score < 80) return 'bg-risk-severe/10 text-risk-severe border-risk-severe/20'
  return 'bg-risk-fatal/10 text-risk-fatal border-risk-fatal/20'
}
