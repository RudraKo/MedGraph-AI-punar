import type { ElementDefinition } from 'cytoscape'

import type { InteractionPair } from '../types/interactions'
import { severityColorMap } from './severity'

export const buildGraphElements = (
  drugs: string[],
  interactions: InteractionPair[],
): ElementDefinition[] => {
  const nodeSet = new Set(drugs.map((drug) => drug.toUpperCase()))

  interactions.forEach((interaction) => {
    nodeSet.add(interaction.drug_a.toUpperCase())
    nodeSet.add(interaction.drug_b.toUpperCase())
  })

  const nodes: ElementDefinition[] = Array.from(nodeSet).map((drug) => ({
    data: { id: drug, label: drug },
  }))

  const edges: ElementDefinition[] = interactions.map((interaction, index) => ({
    data: {
      id: `edge-${interaction.drug_a}-${interaction.drug_b}-${index}`,
      source: interaction.drug_a.toUpperCase(),
      target: interaction.drug_b.toUpperCase(),
      severity: interaction.severity,
      explanation: interaction.explanation,
      color: severityColorMap[interaction.severity],
    },
  }))

  return [...nodes, ...edges]
}
