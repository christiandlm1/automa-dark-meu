export interface ExportProfile {
  id: string
  name: string
  description: string
  format: 'mp4' | 'mov' | 'mkv'
  resolution: string // e.g., '1080x1920'
  fps: number
  video_codec: string
  audio_codec: string
  video_bitrate: string // e.g., '5M'
  audio_bitrate: string // e.g., '192k'
  preset: string // e.g., 'fast', 'medium', 'slow'
  created_at: string
  updated_at: string
}

export type ExportProfileCreate = Omit<ExportProfile, 'id' | 'created_at' | 'updated_at'>
export type ExportProfileUpdate = Partial<ExportProfileCreate>
