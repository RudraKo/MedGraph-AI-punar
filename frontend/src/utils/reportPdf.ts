import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'

import type { DashboardWorkflowState } from '../types/workflow'

const formatDateForFilename = (isoDate: string) =>
  new Date(isoDate)
    .toISOString()
    .replace(/[:.]/g, '-')
    .replace('T', '_')
    .slice(0, 19)

export const exportRiskReportPdf = (workflow: DashboardWorkflowState): string => {
  const doc = new jsPDF({ unit: 'pt', format: 'a4' })
  const pageWidth = doc.internal.pageSize.getWidth()

  doc.setFillColor(31, 123, 128)
  doc.rect(0, 0, pageWidth, 78, 'F')

  doc.setTextColor(255, 255, 255)
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(17)
  doc.text('MediGraph.AI Clinical Risk Report', 42, 44)

  doc.setFont('helvetica', 'normal')
  doc.setFontSize(10)
  doc.text(`Generated: ${new Date(workflow.createdAt).toLocaleString()}`, 42, 62)

  doc.setTextColor(17, 24, 39)
  doc.setFontSize(12)
  doc.setFont('helvetica', 'bold')
  doc.text('Summary', 42, 108)

  doc.setFont('helvetica', 'normal')
  doc.setFontSize(10)
  doc.text(`Execution Mode: ${workflow.executionMode === 'queued' ? 'Queued workers' : 'Synchronous API'}`, 42, 126)
  doc.text(`Medications: ${workflow.extractedDrugs.length}`, 42, 142)
  doc.text(`Risk Score: ${workflow.interactionAnalysis.risk_score}`, 42, 158)
  doc.text(`Clinical Band: ${workflow.interactionAnalysis.clinical_band}`, 42, 174)

  autoTable(doc, {
    startY: 196,
    head: [['Drug A', 'Drug B', 'Severity', 'Explanation']],
    body:
      workflow.interactionAnalysis.interactions.length > 0
        ? workflow.interactionAnalysis.interactions.map((item) => [
            item.drug_a,
            item.drug_b,
            item.severity,
            item.explanation,
          ])
        : [['-', '-', '-', 'No known interactions detected']],
    styles: {
      fontSize: 9,
      cellPadding: 6,
      textColor: [30, 41, 59],
      valign: 'middle',
    },
    headStyles: {
      fillColor: [15, 23, 42],
      textColor: [255, 255, 255],
      fontStyle: 'bold',
    },
    theme: 'striped',
    margin: { left: 42, right: 42 },
    columnStyles: {
      3: { cellWidth: 220 },
    },
  })

  const scheduleTitleY = (doc as jsPDF & { lastAutoTable?: { finalY?: number } }).lastAutoTable?.finalY ?? 360
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(12)
  doc.text('Optimized Medication Timeline', 42, scheduleTitleY + 26)

  autoTable(doc, {
    startY: scheduleTitleY + 36,
    head: [['Time', 'Medications']],
    body:
      workflow.schedule.schedule.length > 0
        ? workflow.schedule.schedule.map((slot) => [slot.time, slot.medications.join(', ')])
        : [['-', 'No timeline generated']],
    styles: {
      fontSize: 9,
      cellPadding: 6,
      textColor: [30, 41, 59],
      valign: 'middle',
    },
    headStyles: {
      fillColor: [30, 58, 138],
      textColor: [255, 255, 255],
      fontStyle: 'bold',
    },
    theme: 'grid',
    margin: { left: 42, right: 42 },
  })

  const notesY = ((doc as jsPDF & { lastAutoTable?: { finalY?: number } }).lastAutoTable?.finalY ?? 560) + 24
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(11)
  doc.text('Scheduling Notes', 42, notesY)
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(9)
  doc.text(workflow.schedule.notes, 42, notesY + 16, { maxWidth: pageWidth - 84 })

  const filename = `medigraph-risk-report-${formatDateForFilename(workflow.createdAt)}.pdf`
  doc.save(filename)
  return filename
}
