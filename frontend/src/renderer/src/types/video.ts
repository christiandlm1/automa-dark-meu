export interface Video {
  id: string
  project_id: string
  name: string
  original_path: string
  project_path: string
  thumbnail_path?: string
  duration?: number
  fps?: number
  width?: number
  height?: number
  resolution?: string
  codec?: string
  bitrate?: number
  size_bytes: number
  hash?: string
  status: 'pending' | 'scanned' | 'error'
  notes?: string
  imported_at: string
  created_at: string
}

export interface VideoImportRequest {
  project_id: string
  file_paths: string[]
}

export interface VideoUpdate {
  notes?: string
  status?: 'pending' | 'scanned' | 'error'
}

export interface VideoListResponse {
  videos: Video[]
  total: number
}
