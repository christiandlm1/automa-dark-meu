export interface Log {
  id: string
  project_id?: string
  level: 'info' | 'warning' | 'error'
  action: string
  message: string
  details?: string // JSON string
  created_at: string
}

export interface LogCreate {
  project_id?: string
  level: 'info' | 'warning' | 'error'
  action: string
  message: string
  details?: string
}

export interface LogListResponse {
  logs: Log[]
  total: number
}
