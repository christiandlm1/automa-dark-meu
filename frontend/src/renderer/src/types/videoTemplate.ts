export interface PipelineNode {
  type:
    | 'import'
    | 'crop'
    | 'zoom'
    | 'color'
    | 'sharpness'
    | 'export'
    | 'metadatacleaner'
    | 'background'
    | 'subtitle'
  config: Record<string, any>
}

export interface VideoTemplate {
  id: string
  name: string
  description: string | null
  category: string | null
  pipeline_config: PipelineNode[]
  versions_history?: Array<{ version: number; updated_at: string; pipeline_config: PipelineNode[] }>
  created_at: string
  updated_at: string
  is_active: boolean
}

export interface VideoTemplateCreate {
  name: string
  description?: string
  category?: string
  pipeline_config: PipelineNode[]
}

export interface VideoTemplateUpdate {
  name?: string
  description?: string
  category?: string
  pipeline_config?: PipelineNode[]
  is_active?: boolean
}

export interface VideoTemplateListResponse {
  templates: VideoTemplate[]
  total: number
}
