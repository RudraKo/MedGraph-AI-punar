export type JobLifecycleStatus = 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE' | 'RETRY' | 'REVOKED'

export interface JobAcceptedPayload {
  job_id: string
  status: JobLifecycleStatus | string
  job_type: string
}

export interface JobStatusPayload<T = unknown> {
  job_id: string
  status: JobLifecycleStatus | string
  ready: boolean
  result?: T
  error?: string
}
