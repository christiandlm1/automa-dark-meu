import { api, API_BASE_URL } from './api'

export interface Asset {
  id: string
  name: string
  type: string
  category: string
  file_path: string
  file_size: number
  mime_type: string
  created_at: string
  usage_count?: number
  is_favorite?: boolean
  tags?: string[]
  file_hash?: string
}

export const assetService = {
  getAssets: async (type?: string, category?: string): Promise<Asset[]> => {
    const params = new URLSearchParams()
    if (type) params.append('type', type)
    if (category) params.append('category', category)

    return api.get<Asset[]>(`/assets?${params.toString()}`)
  },

  uploadAssets: async (
    files: FileList | File[],
    type: string,
    category: string,
    onProgress?: (percent: number) => void
  ): Promise<Asset[]> => {
    return new Promise((resolve, reject) => {
      const formData = new FormData()
      Array.from(files).forEach((file) => {
        formData.append('files', file)
      })
      formData.append('type', type)
      formData.append('category', category)

      const xhr = new XMLHttpRequest()
      xhr.open('POST', `${API_BASE_URL}/assets/upload`)

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable && onProgress) {
          const percentCompleted = Math.round((event.loaded * 100) / event.total)
          onProgress(percentCompleted)
        }
      }

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(JSON.parse(xhr.responseText))
        } else {
          reject(new Error(xhr.responseText || 'Upload failed'))
        }
      }

      xhr.onerror = () => reject(new Error('Network error during upload'))

      xhr.send(formData)
    })
  },

  updateAsset: async (id: string, payload: Partial<Asset>): Promise<Asset> => {
    return api.put<Asset>(`/assets/${id}`, payload)
  },

  getAssetUsage: async (id: string): Promise<{ templates: any[]; projects: any[] }> => {
    return api.get<{ templates: any[]; projects: any[] }>(`/assets/${id}/usage`)
  },

  deleteAsset: async (id: string): Promise<void> => {
    return api.delete(`/assets/${id}`)
  }
}
