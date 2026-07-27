import { api } from './api'
import { Video, VideoImportRequest, VideoUpdate, VideoListResponse } from '../types/video'

export const videoService = {
  importVideos: async (data: VideoImportRequest): Promise<Video[]> => {
    return api.post<Video[]>('/videos/import', data)
  },

  uploadFiles: async (projectId: string, files: File[]): Promise<Video[]> => {
    const formData = new FormData()
    formData.append('project_id', projectId)
    files.forEach((file) => formData.append('files', file))

    const res = await fetch('/api/videos/upload', {
      method: 'POST',
      body: formData
    })
    if (!res.ok) {
      const errText = await res.text()
      throw new Error(errText || 'Falha no upload dos vídeos')
    }
    return res.json()
  },

  listByProject: async (projectId: string, skip = 0, limit = 100): Promise<VideoListResponse> => {
    return api.get<VideoListResponse>(`/videos/project/${projectId}?skip=${skip}&limit=${limit}`)
  },

  getById: async (id: string): Promise<Video> => {
    return api.get<Video>(`/videos/${id}`)
  },

  update: async (id: string, data: VideoUpdate): Promise<Video> => {
    return api.put<Video>(`/videos/${id}`, data)
  },

  delete: async (id: string): Promise<void> => {
    return api.delete<void>(`/videos/${id}`)
  },

  scanVideo: async (id: string): Promise<Video> => {
    return api.post<Video>(`/videos/${id}/scan`)
  },

  scanPending: async (projectId?: string): Promise<Video[]> => {
    const query = projectId ? `?project_id=${projectId}` : ''
    return api.post<Video[]>(`/videos/scan-pending${query}`)
  }
}
