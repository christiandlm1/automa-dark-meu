export interface Setting {
  id: string
  key: string
  value: string
  type: 'string' | 'number' | 'boolean'
  category: 'general' | 'performance' | 'paths'
  updated_at: string
}

export interface SettingCreate {
  key: string
  value: string
  type: 'string' | 'number' | 'boolean'
  category: 'general' | 'performance' | 'paths'
}

export interface SettingUpdate {
  value: string
}

export interface SettingListResponse {
  settings: Setting[]
  total: number
}

export interface AppSettings {
  language: string
  theme: string
  default_projects_dir: string
  max_processes: number
  max_cpu_usage: number
  max_ram_usage: number
  max_gpu_usage: number
  max_workers: number
  process_priority: 'Baixa' | 'Normal' | 'Alta'
}
