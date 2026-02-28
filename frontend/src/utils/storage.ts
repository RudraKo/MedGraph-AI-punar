import type { DashboardWorkflowState } from '../types/workflow'

const STORAGE_KEY = 'medigraph:latest-workflow'

export const saveWorkflow = (payload: DashboardWorkflowState): void => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
}

export const loadWorkflow = (): DashboardWorkflowState | null => {
  const rawValue = localStorage.getItem(STORAGE_KEY)
  if (!rawValue) return null

  try {
    return JSON.parse(rawValue) as DashboardWorkflowState
  } catch {
    return null
  }
}
