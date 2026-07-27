export interface GPUInfo {
  name: string
  manufacturer?: string
  vram_total_mb?: number
  vram_used_mb?: number
  vram_free_mb?: number
  gpu_load_percent?: number
  temperature_c?: number
  vram_bytes?: number
  status?: string
}

export interface Hardware {
  id: string
  cpu_name: string
  cpu_cores: number
  cpu_threads: number
  ram_total_gb: number
  gpu_name?: string
  gpu_memory_gb?: number
  os_name: string
  os_version: string
  detected_at: string
}

export interface HardwareMonitorResponse {
  cpu_percent: number
  cpu_per_core: number[]
  ram: {
    used_percent: number
    available_gb: number
    total_gb: number
  }
  gpu?: {
    name: string
    load_percent: number
    vram_used_percent: number
    vram_total_gb: number
    vram_used_gb: number
    temperature_c?: number
  }
  disk: {
    used_percent: number
    free_gb: number
    total_gb: number
  }
}
