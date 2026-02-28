import { useState } from 'react'

import type { MedicationDosageInput } from '../../types/schedule'

interface MedicationComposerProps {
  dosages: MedicationDosageInput[]
  onChange: (next: MedicationDosageInput[]) => void
}

const normalize = (name: string) => name.trim().toUpperCase()

export const MedicationComposer = ({ dosages, onChange }: MedicationComposerProps) => {
  const [newDrug, setNewDrug] = useState('')
  const [newFrequency, setNewFrequency] = useState(1)

  const handleAdd = () => {
    const normalizedDrug = normalize(newDrug)
    if (!normalizedDrug) return

    const existing = dosages.find((item) => item.drug_name === normalizedDrug)
    if (existing) {
      onChange(
        dosages.map((item) =>
          item.drug_name === normalizedDrug ? { ...item, frequency: Math.max(item.frequency, newFrequency) } : item,
        ),
      )
    } else {
      onChange([...dosages, { drug_name: normalizedDrug, frequency: newFrequency }])
    }

    setNewDrug('')
    setNewFrequency(1)
  }

  const handleDelete = (drugName: string) => {
    onChange(dosages.filter((item) => item.drug_name !== drugName))
  }

  const updateFrequency = (drugName: string, nextFrequency: number) => {
    onChange(
      dosages.map((item) =>
        item.drug_name === drugName ? { ...item, frequency: Math.max(1, Math.floor(nextFrequency)) } : item,
      ),
    )
  }

  return (
    <div className="bg-surface-light border border-surface-border rounded-xl p-6 shadow-card">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-brand-blue/10 rounded-lg">
          <svg className="w-5 h-5 text-brand-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
        <div>
          <p className="section-title">Medication Composer</p>
          <p className="subtle-text">Review extracted drugs, add missing entries, and set daily frequency.</p>
        </div>
      </div>

      <div className="mt-6 p-4 bg-surface-muted rounded-xl border border-surface-border grid gap-3 sm:grid-cols-[1fr_120px_auto] items-center">
        <div className="relative">
          <input
            value={newDrug}
            onChange={(event) => setNewDrug(event.target.value)}
            placeholder="Type medication name..."
            className="w-full rounded-lg border border-gray-300 pl-10 pr-3 py-2.5 text-sm text-brand-navy outline-none transition-all focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 bg-white"
          />
          <svg className="w-4 h-4 text-gray-400 absolute left-3.5 top-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </div>
        <div className="relative">
          <input
            type="number"
            min={1}
            max={6}
            value={newFrequency}
            onChange={(event) => setNewFrequency(Number(event.target.value || 1))}
            className="w-full rounded-lg border border-gray-300 pl-10 pr-3 py-2.5 text-sm text-brand-navy outline-none transition-all focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 bg-white"
          />
          <span className="text-xs text-gray-400 font-medium absolute left-3 top-3.5">Freq</span>
        </div>
        <button type="button" onClick={handleAdd} className="btn-primary py-2.5 px-6 whitespace-nowrap">
          Add Drug
        </button>
      </div>

      <div className="mt-6 space-y-3">
        {dosages.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center bg-gray-50/50 rounded-xl border border-dashed border-gray-200">
            <p className="text-sm font-medium text-gray-500">No active medications in regimen.</p>
            <p className="text-xs text-gray-400 mt-1">Add a drug above to begin interaction analysis.</p>
          </div>
        ) : (
          dosages.map((item) => (
            <div
              key={item.drug_name}
              className="group flex items-center justify-between gap-4 rounded-xl border border-surface-border bg-white px-4 py-3 shadow-sm transition-all hover:border-brand-blue/30 hover:shadow-md"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-brand-blue/10 flex items-center justify-center text-brand-blue font-bold text-xs uppercase tracking-wider">
                  {item.drug_name.charAt(0)}{item.drug_name.charAt(1)}
                </div>
                <p className="text-sm font-bold text-brand-navy uppercase tracking-wide">{item.drug_name}</p>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 bg-surface-muted px-3 py-1.5 rounded-lg border border-surface-border">
                  <span className="text-xs font-semibold text-gray-500 uppercase">Daily</span>
                  <input
                    type="number"
                    min={1}
                    max={6}
                    value={item.frequency}
                    onChange={(event) => updateFrequency(item.drug_name, Number(event.target.value || 1))}
                    className="w-12 text-center rounded-md border border-gray-300 py-1 text-sm font-bold text-brand-navy outline-none focus:border-brand-blue focus:ring-1 focus:ring-brand-blue"
                  />
                </div>
                <button
                  type="button"
                  onClick={() => handleDelete(item.drug_name)}
                  className="rounded-lg p-2 text-gray-400 hover:bg-risk-fatal/10 hover:text-risk-fatal transition-colors focus:outline-none focus:ring-2 focus:ring-risk-fatal/20"
                  aria-label="Remove medication"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
