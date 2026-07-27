import { api } from './api'
import { Setting, SettingCreate, SettingUpdate, SettingListResponse } from '../types/settings'

export const settingsService = {
  create: async (data: SettingCreate): Promise<Setting> => {
    return api.post<Setting>('/settings', data)
  },

  list: async (category?: string): Promise<SettingListResponse> => {
    const query = category ? `?category=${category}` : ''
    return api.get<SettingListResponse>(`/settings${query}`)
  },

  getByKey: async (key: string): Promise<Setting> => {
    return api.get<Setting>(`/settings/key/${key}`)
  },

  getById: async (id: string): Promise<Setting> => {
    return api.get<Setting>(`/settings/${id}`)
  },

  updateByKey: async (key: string, data: SettingUpdate): Promise<Setting> => {
    return api.put<Setting>(`/settings/key/${key}`, data)
  },

  update: async (id: string, data: SettingUpdate): Promise<Setting> => {
    return api.put<Setting>(`/settings/${id}`, data)
  },

  delete: async (id: string): Promise<void> => {
    return api.delete<void>(`/settings/${id}`)
  }
}
