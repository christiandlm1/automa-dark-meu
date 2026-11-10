import { api } from './api'
import { Job, JobCreate, JobListResponse, JobStats } from '../types/job'

export const jobService = {
  enqueue: async (data: JobCreate): Promise<Job> => {
    return api.post<Job>('/jobs', data)
  },

  get: async (id: string): Promise<Job> => {
    return api.get<Job>(`/jobs/${id}`)
  },

  listByProject: async (projectId: string): Promise<JobListResponse> => {
    return api.get<JobListResponse>(`/jobs/project/${projectId}`)
  },

  pause: async (id: string): Promise<Job> => {
    return api.post<Job>(`/jobs/${id}/pause`)
  },

  resume: async (id: string): Promise<Job> => {
    return api.post<Job>(`/jobs/${id}/resume`)
  },

  cancel: async (id: string): Promise<Job> => {
    return api.post<Job>(`/jobs/${id}/cancel`)
  },

  getStats: async (projectId: string): Promise<JobStats> => {
    return api.get<JobStats>(`/jobs/project/${projectId}/stats`)
  },

  reprocess: async (id: string): Promise<Job> => {
    return api.post<Job>(`/jobs/${id}/reprocess`)
  },

  clearQueue: async (projectId: string): Promise<{ removed: number; kept_running: number }> => {
    return api.delete<{ removed: number; kept_running: number }>(`/jobs/project/${projectId}/queue`)
  },

  preview: async (data: {
    video_id: string
    template_id: string
    start_time: number
    end_time: number
  }): Promise<{ preview_url: string }> => {
    return api.post<{ preview_url: string }>('/jobs/preview', data)
  }
}
