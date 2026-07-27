import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { Project } from '../types/project'
import { Video } from '../types/video'
import { projectService } from '../services/projectService'
import { videoService } from '../services/videoService'
import { useToast } from './ToastContext'

interface ProjectContextType {
  activeProject: Project | null
  videos: Video[]
  loading: boolean
  totalVideos: number
  totalBytes: number
  processedCount: number
  pendingCount: number
  errorCount: number
  loadProject: (id: string) => Promise<void>
  closeProject: () => void
  refreshProjectData: () => Promise<void>
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined)

export const ProjectProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeProject, setActiveProject] = useState<Project | null>(null)
  const [videos, setVideos] = useState<Video[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const { showToast } = useToast()

  // Calculate project statistics
  const totalVideos = videos.length
  const totalBytes = videos.reduce((acc, v) => acc + (v.size_bytes || 0), 0)
  const processedCount = videos.filter((v) => v.status === 'scanned').length
  const pendingCount = videos.filter((v) => v.status === 'pending').length
  const errorCount = videos.filter((v) => v.status === 'error').length

  const refreshProjectData = useCallback(async () => {
    if (!activeProject) return
    try {
      const response = await videoService.listByProject(activeProject.id, 0, 500)
      setVideos(response.videos)
    } catch (err) {
      console.error('Error refreshing project videos:', err)
    }
  }, [activeProject])

  const loadProject = useCallback(
    async (id: string) => {
      setLoading(true)
      try {
        const proj = await projectService.open(id)
        setActiveProject(proj)

        // Load videos in project
        const response = await videoService.listByProject(proj.id, 0, 500)
        setVideos(response.videos)

        localStorage.setItem('automa_active_project_id', id)
        showToast(`Projeto "${proj.name}" carregado com sucesso`, 'success')
      } catch (err) {
        showToast(err instanceof Error ? err.message : 'Falha ao carregar projeto', 'error')
        setActiveProject(null)
        setVideos([])
        localStorage.removeItem('automa_active_project_id')
      } finally {
        setLoading(false)
      }
    },
    [showToast]
  )

  const closeProject = useCallback(() => {
    setActiveProject(null)
    setVideos([])
    localStorage.removeItem('automa_active_project_id')
    showToast('Projeto fechado', 'info')
  }, [showToast])

  // Try auto-opening last project or default project on start (runs once on mount)
  useEffect(() => {
    const initProject = async () => {
      const lastId = localStorage.getItem('automa_active_project_id')
      if (lastId) {
        try {
          await loadProject(lastId)
          return
        } catch {
          localStorage.removeItem('automa_active_project_id')
        }
      }

      try {
        const res = await projectService.list(0, 10)
        if (res.projects && res.projects.length > 0) {
          await loadProject(res.projects[0].id)
        } else {
          const newP = await projectService.create({
            name: 'Projeto Principal',
            description: 'Projeto padrão de processamento em lote',
            path: 'default_workspace'
          })
          await loadProject(newP.id)
        }
      } catch (err) {
        console.error('Failed auto-loading project:', err)
      }
    }

    initProject()
  }, [])

  return (
    <ProjectContext.Provider
      value={{
        activeProject,
        videos,
        loading,
        totalVideos,
        totalBytes,
        processedCount,
        pendingCount,
        errorCount,
        loadProject,
        closeProject,
        refreshProjectData
      }}
    >
      {children}
    </ProjectContext.Provider>
  )
}

export const useProject = () => {
  const context = useContext(ProjectContext)
  if (!context) {
    throw new Error('useProject must be used within a ProjectProvider')
  }
  return context
}
