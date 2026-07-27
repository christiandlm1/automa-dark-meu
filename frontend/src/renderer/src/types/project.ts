export interface Project {
  id: string
  name: string
  description?: string
  path: string
  category?: string
  database_path: string
  created_at: string
  updated_at: string
  status: string
}

export interface ProjectCreate {
  name: string
  description?: string
  path?: string // If empty, server defaults to projects directory
  category?: string
}

export interface ProjectUpdate {
  name?: string
  description?: string
  category?: string
  status?: string
}

export interface ProjectListResponse {
  projects: Project[]
  total: number
}

export interface RecentProject {
  id: string
  project_id: string
  name: string
  path: string
  last_opened_at: string
}
