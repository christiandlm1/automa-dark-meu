import { api } from './api'
import { Log, LogCreate, LogListResponse } from '../types/log'

export const logService = {
  create: async (data: LogCreate): Promise<Log> => {
    return api.post<Log>('/logs', data)
  },

  list: async (
    skip = 0,
    limit = 100,
    projectId?: string,
    level?: string,
    action?: string
  ): Promise<LogListResponse> => {
    let params = `skip=${skip}&limit=${limit}`
    if (projectId) params += `&project_id=${projectId}`
    if (level) params += `&level=${level}`
    if (action) params += `&action=${action}`
    return api.get<LogListResponse>(`/logs?${params}`)
  },

  getRecent: async (limit = 50): Promise<Log[]> => {
    return api.get<Log[]>(`/logs/recent?limit=${limit}`)
  }
}
