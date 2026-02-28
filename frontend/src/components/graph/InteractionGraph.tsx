import { useEffect, useRef, useState } from 'react'
import cytoscape from 'cytoscape'
import type { Core } from 'cytoscape'

import type { InteractionPair } from '../../types/interactions'
import { buildGraphElements } from '../../utils/graph'

interface InteractionGraphProps {
  drugs: string[]
  interactions: InteractionPair[]
}

export const InteractionGraph = ({ drugs, interactions }: InteractionGraphProps) => {
  const graphRef = useRef<HTMLDivElement | null>(null)
  const cyRef = useRef<Core | null>(null)
  const [selectedEdgeExplanation, setSelectedEdgeExplanation] = useState<string | null>(null)

  useEffect(() => {
    if (!graphRef.current) return

    const elements = buildGraphElements(drugs, interactions)

    if (cyRef.current) {
      cyRef.current.destroy()
    }

    cyRef.current = cytoscape({
      container: graphRef.current,
      elements,
      layout: {
        name: 'cose',
        animate: true,
      },
      style: [
        {
          selector: 'node',
          style: {
            label: 'data(label)',
            'background-color': '#FFFFFF',
            color: '#0F233E',
            'font-family': 'Inter, sans-serif',
            'font-size': '12px',
            'font-weight': 'bold',
            'text-wrap': 'wrap',
            'text-max-width': '86px',
            'text-valign': 'bottom',
            'text-margin-y': 8,
            width: '44px',
            height: '44px',
            'border-width': '2px',
            'border-color': '#2B61B1',
            'shadow-color': '#000000',
            'shadow-blur': 10,
            'shadow-opacity': 0.05,
            'transition-property': 'background-color, transform, border-color',
            'transition-duration': 0.2,
          } as unknown as cytoscape.Css.Node,
        },
        {
          selector: 'node:active',
          style: {
            'background-color': '#F8F9FA',
            'border-color': '#059669',
            width: '50px',
            height: '50px',
          } as unknown as cytoscape.Css.Node,
        },
        {
          selector: 'edge',
          style: {
            width: '3px',
            'line-color': 'data(color)',
            'target-arrow-color': 'data(color)',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            opacity: 0.8,
            label: 'data(severity)',
            'font-size': '10px',
            'font-family': 'Inter, sans-serif',
            'font-weight': 'bold',
            color: 'data(color)',
            'text-background-opacity': 1,
            'text-background-color': '#FFFFFF',
            'text-background-padding': '2px',
            'text-background-shape': 'roundrectangle',
            'text-border-color': 'data(color)',
            'text-border-width': 1,
            'text-border-opacity': 0.5,
          } as unknown as cytoscape.Css.Edge,
        },
      ],
    })

    cyRef.current.on('tap', 'edge', (event) => {
      const explanation = event.target.data('explanation') as string | undefined
      setSelectedEdgeExplanation(explanation ?? null)
    })

    cyRef.current.on('tap', 'node', () => {
      setSelectedEdgeExplanation(null)
    })

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy()
        cyRef.current = null
      }
    }
  }, [drugs, interactions])

  return (
    <div className="bg-surface-light border border-surface-border rounded-xl p-6 shadow-card flex flex-col relative w-full h-full min-h-[500px]">
      <div className="flex justify-between items-center mb-4">
        <div>
          <p className="section-title">Safety Interaction Graph</p>
          <p className="subtle-text mt-1">N-dimensional visualization of detected medication conflicts.</p>
        </div>
      </div>

      <div ref={graphRef} className="flex-1 w-full rounded-xl border border-surface-border bg-surface-muted relative z-0" />

      {/* Floating Action Bar */}
      <div className="absolute top-[88px] right-10 flex space-x-2 bg-surface-light/80 backdrop-blur-md border border-surface-border shadow-md rounded-full px-4 py-2 z-10 transition-all pointer-events-none">
        <span className="text-brand-navy text-xs font-bold tracking-wide flex items-center gap-2">
          <svg className="w-4 h-4 text-brand-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Interactive Canvas
        </span>
      </div>

      <div className="mt-5 flex flex-wrap items-center gap-3 text-xs font-bold text-gray-500 uppercase tracking-wider">
        <LegendChip tone="bg-risk-safe" label="Mild" />
        <LegendChip tone="bg-risk-moderate" label="Moderate" />
        <LegendChip tone="bg-risk-severe" label="Severe" />
        <LegendChip tone="bg-risk-fatal" label="Contraindicated" />
      </div>
      {selectedEdgeExplanation ? (
        <div className="mt-4 rounded-xl border border-brand-blue/20 bg-brand-blue/5 p-4 text-sm text-brand-navy flex items-start gap-3 shadow-sm animate-fade-in">
          <svg className="w-5 h-5 text-brand-blue shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <span className="font-bold text-brand-blue block mb-1">Interaction Detail</span>
            <span className="text-gray-600 leading-relaxed">{selectedEdgeExplanation}</span>
          </div>
        </div>
      ) : null}
    </div>
  )
}

interface LegendChipProps {
  tone: string
  label: string
}

const LegendChip = ({ tone, label }: LegendChipProps) => (
  <span className="inline-flex items-center gap-2 rounded-full border border-surface-border bg-surface-light px-3 py-1 shadow-sm">
    <span className={`h-2.5 w-2.5 rounded-full ${tone}`} />
    {label}
  </span>
)
