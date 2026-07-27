import { api } from './api'
import { HistoryListResponse } from '../types/history'

export const historyService = {
  listByProject: async (projectId: string, skip = 0, limit = 100): Promise<HistoryListResponse> => {
    return api.get<HistoryListResponse>(`/history/project/${projectId}?skip=${skip}&limit=${limit}`)
  },

  clear: async (projectId: string): Promise<{ detail: string }> => {
    return api.delete<{ detail: string }>(`/history/project/${projectId}`)
  }
}
