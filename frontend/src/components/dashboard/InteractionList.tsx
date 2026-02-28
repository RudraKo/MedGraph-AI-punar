import { useMemo, useState } from 'react'

import type { InteractionPair } from '../../types/interactions'
import type { SeverityLevel } from '../../types/api'
import { severityBadgeClass } from '../../utils/severity'

interface InteractionListProps {
  interactions: InteractionPair[]
}

export const InteractionList = ({ interactions }: InteractionListProps) => {
  const [query, setQuery] = useState('')
  const [severityFilter, setSeverityFilter] = useState<SeverityLevel | 'all'>('all')

  const filteredInteractions = useMemo(() => {
    return interactions.filter((item) => {
      const matchesSeverity = severityFilter === 'all' ? true : item.severity === severityFilter
      const normalizedQuery = query.trim().toLowerCase()
      const matchesQuery =
        normalizedQuery.length === 0
          ? true
          : [item.drug_a, item.drug_b, item.explanation].some((value) =>
            value.toLowerCase().includes(normalizedQuery),
          )

      return matchesSeverity && matchesQuery
    })
  }, [interactions, query, severityFilter])

  if (interactions.length === 0) {
    return (
      <div className="bg-surface-light border border-surface-border rounded-xl p-6 shadow-card">
        <p className="section-title">Detected Interactions</p>
        <div className="mt-4 flex flex-col items-center justify-center p-8 bg-surface-muted rounded-xl border border-dashed border-surface-border">
          <svg className="w-12 h-12 text-risk-safe/50 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm font-medium text-gray-500 text-center text-risk-safe">
            Regimen is stable. No critical interactions detected in current pipeline.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-surface-light border border-surface-border rounded-xl p-6 shadow-card">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="section-title">Detected Interactions</p>
          <p className="subtle-text mt-1">
            {filteredInteractions.length} of {interactions.length} interaction(s) shown
          </p>
        </div>

        <div className="flex flex-wrap gap-3">
          <select
            value={severityFilter}
            onChange={(event) => setSeverityFilter(event.target.value as SeverityLevel | 'all')}
            className="rounded-lg border border-surface-border bg-surface-light px-3 py-2 text-sm text-brand-navy outline-none focus:ring-2 focus:ring-brand-blue focus:border-brand-blue transition-all"
          >
            <option value="all">All severities</option>
            <option value="mild">Mild</option>
            <option value="moderate">Moderate</option>
            <option value="severe">Severe</option>
            <option value="contraindicated">Contraindicated</option>
          </select>

          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search medication..."
            className="rounded-lg border border-surface-border bg-surface-light px-4 py-2 text-sm text-brand-navy outline-none focus:ring-2 focus:ring-brand-blue focus:border-brand-blue transition-all"
          />
        </div>
      </div>

      <div className="mt-5 space-y-3">
        {filteredInteractions.map((item, index) => (
          <div key={`${item.drug_a}-${item.drug_b}-${index}`} className="rounded-xl border border-surface-border bg-surface-light p-4 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="text-sm font-bold text-brand-navy font-mono">
                {item.drug_a} + {item.drug_b}
              </p>
              <span
                className={`rounded-full border px-3 py-1 text-xs font-bold uppercase tracking-wider ${severityBadgeClass[item.severity]}`}
              >
                {item.severity}
              </span>
            </div>
            <p className="mt-2 text-sm text-gray-600 leading-relaxed">{item.explanation}</p>
          </div>
        ))}

        {filteredInteractions.length === 0 ? (
          <div className="rounded-xl border border-surface-border bg-surface-muted p-4 text-center text-sm text-gray-500">
            No interactions match the current filters.
          </div>
        ) : null}
      </div>
    </div>
  )
}
