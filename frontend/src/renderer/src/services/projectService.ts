import { api } from './api'
import { Project, ProjectCreate, ProjectUpdate, ProjectListResponse } from '../types/project'

export const projectService = {
  create: async (data: ProjectCreate): Promise<Project> => {
    return api.post<Project>('/projects', data)
  },

  getById: async (id: string): Promise<Project> => {
    return api.get<Project>(`/projects/${id}`)
  },

  list: async (skip = 0, limit = 100): Promise<ProjectListResponse> => {
    return api.get<ProjectListResponse>(`/projects?skip=${skip}&limit=${limit}`)
  },

  getRecent: async (limit = 10): Promise<any[]> => {
    return api.get<any[]>(`/projects/recent?limit=${limit}`)
  },

  search: async (query: string, skip = 0, limit = 50): Promise<ProjectListResponse> => {
    return api.get<ProjectListResponse>(
      `/projects/search?q=${encodeURIComponent(query)}&skip=${skip}&limit=${limit}`
    )
  },

  update: async (id: string, data: ProjectUpdate): Promise<Project> => {
    return api.put<Project>(`/projects/${id}`, data)
  },

  delete: async (id: string): Promise<void> => {
    return api.delete<void>(`/projects/${id}`)
  },

  open: async (id: string): Promise<Project> => {
    return api.post<Project>(`/projects/${id}/open`)
  }
}
