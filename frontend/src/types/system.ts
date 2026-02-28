export interface ReadinessStatus {
  status: 'ready' | 'degraded'
  dependencies: {
    database: boolean
    cache: boolean
    queue: boolean
    queue_mode: 'enabled' | 'disabled'
  }
}
