import { api } from './api'
import {
  VideoTemplate,
  VideoTemplateCreate,
  VideoTemplateUpdate,
  VideoTemplateListResponse
} from '../types/videoTemplate'

export const videoTemplateService = {
  list: async (
    query?: string,
    category?: string,
    skip = 0,
    limit = 100
  ): Promise<VideoTemplateListResponse> => {
    let url = '/video-templates?'
    const params: string[] = []
    if (query) params.push(`query=${encodeURIComponent(query)}`)
    if (category) params.push(`category=${encodeURIComponent(category)}`)
    params.push(`skip=${skip}`)
    params.push(`limit=${limit}`)
    url += params.join('&')
    return api.get<VideoTemplateListResponse>(url)
  },

  get: async (id: string): Promise<VideoTemplate> => {
    return api.get<VideoTemplate>(`/video-templates/${id}`)
  },

  create: async (data: VideoTemplateCreate): Promise<VideoTemplate> => {
    return api.post<VideoTemplate>('/video-templates', data)
  },

  update: async (id: string, data: VideoTemplateUpdate): Promise<VideoTemplate> => {
    return api.put<VideoTemplate>(`/video-templates/${id}`, data)
  },

  delete: async (id: string): Promise<{ detail: string }> => {
    return api.delete<{ detail: string }>(`/video-templates/${id}`)
  },

  duplicate: async (id: string): Promise<VideoTemplate> => {
    return api.post<VideoTemplate>(`/video-templates/${id}/duplicate`)
  },

  restore: async (id: string, version: number): Promise<VideoTemplate> => {
    return api.post<VideoTemplate>(`/video-templates/${id}/restore/${version}`)
  }
}
