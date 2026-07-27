export interface HistoryRecord {
  id: string
  project_id: string
  video_id: string | null
  video_name: string
  template_id: string | null
  template_name: string
  processed_at: string
  execution_time: number
  status: 'completed' | 'failed'
  log: string | null
  exported_path: string | null
}

export interface HistoryListResponse {
  history: HistoryRecord[]
  total: number
}
