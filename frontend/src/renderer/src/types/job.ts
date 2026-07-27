import { Video } from './video'
import { VideoTemplate } from './videoTemplate'
import { ExportProfile } from './exportProfile'

export type JobStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled' | 'paused'

export interface Job {
  id: string
  project_id: string
  video_id: string
  template_id: string | null
  export_profile_id: string | null
  status: JobStatus
  progress: number
  speed: number
  started_at: string | null
  finished_at: string | null
  estimated_time: number | null
  error_message: string | null
  created_at: string
  updated_at: string

  // Optional nested loads
  video?: Video
  template?: VideoTemplate
  export_profile?: ExportProfile
}

export interface JobCreate {
  project_id: string
  video_id: string
  template_id: string
  export_profile_id: string
}

export interface JobListResponse {
  jobs: Job[]
  total: number
}

export interface JobStats {
  pending: number
  running: number
  completed: number
  failed: number
  cancelled: number
  paused: number
  active_workers: number
  max_workers: number
  priority: 'Baixa' | 'Normal' | 'Alta'
  cache_hits?: number
  cache_misses?: number
  avg_video_time?: number
  processed_today?: number
}
