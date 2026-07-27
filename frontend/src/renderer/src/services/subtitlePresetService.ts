import { SubtitlePreset, SubtitlePresetCreate, SubtitlePresetUpdate } from '../types/subtitlePreset'

const STORAGE_KEY = 'automa_subtitle_presets'

const generateId = () => {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
}

export const subtitlePresetService = {
  list: async (): Promise<SubtitlePreset[]> => {
    const data = localStorage.getItem(STORAGE_KEY)
    return data ? JSON.parse(data) : []
  },

  get: async (id: string): Promise<SubtitlePreset | undefined> => {
    const data = localStorage.getItem(STORAGE_KEY)
    const presets: SubtitlePreset[] = data ? JSON.parse(data) : []
    return presets.find((p) => p.id === id)
  },

  create: async (data: SubtitlePresetCreate): Promise<SubtitlePreset> => {
    const presets = await subtitlePresetService.list()
    const newPreset: SubtitlePreset = {
      ...data,
      id: generateId(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    presets.push(newPreset)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(presets))
    return newPreset
  },

  update: async (id: string, data: SubtitlePresetUpdate): Promise<SubtitlePreset> => {
    const presets = await subtitlePresetService.list()
    const index = presets.findIndex((p) => p.id === id)
    if (index === -1) throw new Error('Preset not found')

    const updatedPreset: SubtitlePreset = {
      ...presets[index],
      ...data,
      updated_at: new Date().toISOString()
    }
    presets[index] = updatedPreset
    localStorage.setItem(STORAGE_KEY, JSON.stringify(presets))
    return updatedPreset
  },

  delete: async (id: string): Promise<{ detail: string }> => {
    const presets = await subtitlePresetService.list()
    const filtered = presets.filter((p) => p.id !== id)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered))
    return { detail: 'Deleted successfully' }
  }
}
