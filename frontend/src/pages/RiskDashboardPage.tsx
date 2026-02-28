import { Suspense, lazy } from 'react'
import { motion } from 'framer-motion'
import { Link, useLocation } from 'react-router-dom'

import { LoadingState } from '../components/common/LoadingState'
import { PageHeader } from '../components/common/PageHeader'
import { InteractionList } from '../components/dashboard/InteractionList'
import { KpiStrip } from '../components/dashboard/KpiStrip'
import { RiskCard } from '../components/dashboard/RiskCard'
import { RiskReportActions } from '../components/dashboard/RiskReportActions'
import { ScheduleTimeline } from '../components/dashboard/ScheduleTimeline'
import { WorkflowMetaCard } from '../components/dashboard/WorkflowMetaCard'
import type { DashboardWorkflowState } from '../types/workflow'
import { loadWorkflow } from '../utils/storage'

const cardMotion = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
}

const RiskAnalyticsChart = lazy(() =>
  import('../components/dashboard/RiskAnalyticsChart').then((module) => ({
    default: module.RiskAnalyticsChart,
  })),
)

const InteractionGraph = lazy(() =>
  import('../components/graph/InteractionGraph').then((module) => ({
    default: module.InteractionGraph,
  })),
)

export const RiskDashboardPage = () => {
  const location = useLocation()
  const routeState = location.state as DashboardWorkflowState | undefined
  const workflow = routeState ?? loadWorkflow()

  if (!workflow) {
    return (
      <section className="bg-surface-light border border-surface-border rounded-xl p-8 shadow-card flex flex-col items-center justify-center min-h-[500px] text-center">
        <div className="w-16 h-16 bg-brand-blue/10 rounded-full flex items-center justify-center mb-6">
          <svg className="w-8 h-8 text-brand-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <PageHeader
          eyebrow="Risk Dashboard"
          title="No Active Analysis Session"
          subtitle="Run a prescription extraction to generate risk analytics and graph visualization."
          className="items-center"
        />
        <div className="mt-8">
          <Link to="/" className="btn-primary inline-flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Return to Upload
          </Link>
        </div>
      </section>
    )
  }

  return (
    <section>
      <PageHeader
        eyebrow="Clinical Insights"
        title="Medication Risk Command Center"
        subtitle={`Analysis generated for ${workflow.extractedDrugs.length} medication(s) using ${workflow.executionMode === 'queued' ? 'queued workers' : 'direct API mode'}.`}
        actions={<RiskReportActions workflow={workflow} />}
      />

      <div className="space-y-5">
        <KpiStrip analysis={workflow.interactionAnalysis} medicationCount={workflow.extractedDrugs.length} />

        <div className="grid gap-5 xl:grid-cols-[1.25fr_1fr]">
          <div className="space-y-5">
            <RiskCard analysis={workflow.interactionAnalysis} />
            <motion.div variants={cardMotion} initial="initial" animate="animate" transition={{ delay: 0.08 }}>
              <InteractionList interactions={workflow.interactionAnalysis.interactions} />
            </motion.div>
            <motion.div variants={cardMotion} initial="initial" animate="animate" transition={{ delay: 0.12 }}>
              <ScheduleTimeline slots={workflow.schedule.schedule} notes={workflow.schedule.notes} />
            </motion.div>
          </div>

          <div className="space-y-5">
            <motion.div variants={cardMotion} initial="initial" animate="animate" transition={{ delay: 0.03 }}>
              <WorkflowMetaCard
                executionMode={workflow.executionMode}
                generatedAt={workflow.createdAt}
                ocr={workflow.ocr}
              />
            </motion.div>
            <motion.div variants={cardMotion} initial="initial" animate="animate" transition={{ delay: 0.06 }}>
              <Suspense fallback={<LoadingState label="Loading risk chart..." />}>
                <RiskAnalyticsChart analysis={workflow.interactionAnalysis} />
              </Suspense>
            </motion.div>
            <motion.div variants={cardMotion} initial="initial" animate="animate" transition={{ delay: 0.1 }}>
              <div className="glass-card">
                <p className="section-title">Interaction Graph</p>
                <p className="subtle-text mt-1">Visual conflict topology across extracted medications.</p>
                <div className="mt-4">
                  <Suspense fallback={<LoadingState label="Rendering interaction graph..." />}>
                    <InteractionGraph
                      drugs={workflow.extractedDrugs}
                      interactions={workflow.interactionAnalysis.interactions}
                    />
                  </Suspense>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  )
}
