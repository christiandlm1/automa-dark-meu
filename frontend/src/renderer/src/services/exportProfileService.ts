import { api } from './api'
import { ExportProfile, ExportProfileCreate, ExportProfileUpdate } from '../types/exportProfile'

// Shape returned/accepted by the backend (schemas/export_profile.py).
interface BackendExportProfile {
  id: string
  name: string
  resolution: string | null
  fps: number | null
  codec: string | null
  bitrate: string | null
  is_custom: boolean
  created_at: string
  updated_at: string
}

// The backend only stores resolution/fps/codec/bitrate. The remaining fields the UI shows
// (format, audio codec/bitrate, preset, description) get defaults when reading.
const fromBackend = (p: BackendExportProfile): ExportProfile => ({
  id: p.id,
  name: p.name,
  description: '',
  format: 'mp4',
  resolution: p.resolution ?? '1080x1920',
  fps: p.fps ?? 30,
  video_codec: p.codec ?? 'h264',
  audio_codec: 'aac',
  video_bitrate: p.bitrate ?? '5M',
  audio_bitrate: '192k',
  preset: 'medium',
  created_at: p.created_at,
  updated_at: p.updated_at
})

const toBackend = (data: ExportProfileUpdate): Record<string, unknown> => {
  const out: Record<string, unknown> = {}
  if (data.name !== undefined) out.name = data.name
  if (data.resolution !== undefined) out.resolution = data.resolution
  if (data.fps !== undefined) out.fps = data.fps
  if (data.video_codec !== undefined) out.codec = data.video_codec
  if (data.video_bitrate !== undefined) out.bitrate = data.video_bitrate
  return out
}

export const exportProfileService = {
  getAll: async (): Promise<ExportProfile[]> => {
    // The backend wraps the list as { profiles, total }; every caller expects a plain array.
    const response = await api.get<{ profiles: BackendExportProfile[]; total: number }>(
      '/export-profiles'
    )
    return response.profiles.map(fromBackend)
  },

  getById: async (id: string): Promise<ExportProfile> => {
    const response = await api.get<BackendExportProfile>(`/export-profiles/${id}`)
    return fromBackend(response)
  },

  create: async (data: ExportProfileCreate): Promise<ExportProfile> => {
    const response = await api.post<BackendExportProfile>('/export-profiles', toBackend(data))
    return fromBackend(response)
  },

  update: async (id: string, data: ExportProfileUpdate): Promise<ExportProfile> => {
    const response = await api.put<BackendExportProfile>(
      `/export-profiles/${id}`,
      toBackend(data)
    )
    return fromBackend(response)
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/export-profiles/${id}`)
  }
}
