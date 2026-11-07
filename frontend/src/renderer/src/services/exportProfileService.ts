import { api } from './api'
import { ExportProfile, ExportProfileCreate, ExportProfileUpdate } from '../types/exportProfile'

export const exportProfileService = {
  getAll: async (): Promise<ExportProfile[]> => {
    // The backend wraps the list as { profiles, total }; every caller expects a plain array.
    const response = await api.get<{ profiles: ExportProfile[]; total: number }>('/export-profiles')
    return response.profiles
  },

  getById: async (id: string): Promise<ExportProfile> => {
    const response = await api.get<ExportProfile>(`/export-profiles/${id}`)
    return response
  },

  create: async (data: ExportProfileCreate): Promise<ExportProfile> => {
    const response = await api.post<ExportProfile>('/export-profiles', data)
    return response
  },

  update: async (id: string, data: ExportProfileUpdate): Promise<ExportProfile> => {
    const response = await api.put<ExportProfile>(`/export-profiles/${id}`, data)
    return response
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/export-profiles/${id}`)
  }
}
