import { api } from './api'
import { Hardware, HardwareMonitorResponse } from '../types/hardware'

export const hardwareService = {
  detect: async (): Promise<Hardware> => {
    return api.post<Hardware>('/hardware/detect')
  },

  getInfo: async (): Promise<Hardware> => {
    return api.get<Hardware>('/hardware/info')
  },

  getRealtime: async (): Promise<HardwareMonitorResponse> => {
    return api.get<HardwareMonitorResponse>('/hardware/realtime')
  }
}
