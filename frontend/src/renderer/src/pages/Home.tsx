import React, { useState, useEffect } from 'react'
import { FolderPlus, FolderOpen, Settings, HelpCircle, FileText } from 'lucide-react'
import { useProject } from '../contexts/ProjectContext'
import { useToast } from '../contexts/ToastContext'
import { projectService } from '../services/projectService'
import { RecentProject } from '../types/project'
import { AutomaLogo } from '../icons/AutomaLogo'
import { Button } from '../components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { NewProjectModal } from '../components/project/NewProjectModal'
import { RecentProjectsList } from '../components/project/RecentProjectsList'
import { useNavigate } from 'react-router-dom'

export const Home: React.FC = () => {
  const navigate = useNavigate()
  const { loadProject } = useProject()
  const { showToast } = useToast()

  const [recentProjects, setRecentProjects] = useState<RecentProject[]>([])
  const [isNewModalOpen, setIsNewModalOpen] = useState(false)
  const [loadingRecents, setLoadingRecents] = useState(false)

  const fetchRecentProjects = async () => {
    setLoadingRecents(true)
    try {
      const recents = await projectService.getRecent()
      setRecentProjects(recents)
    } catch (err) {
      console.error('Error fetching recent projects:', err)
    } finally {
      setLoadingRecents(false)
    }
  }

  useEffect(() => {
    fetchRecentProjects()
  }, [])

  const handleOpenProject = async () => {
    try {
      // In Electron main process, trigger select folder path
      if (window.api && (window.api as any).openDirectory) {
        const folder = await (window.api as any).openDirectory()
        if (folder) {
          showToast('Abrindo projeto selecionado...', 'info')
          const allProjects = await projectService.list(0, 100)
          const matched = allProjects.projects.find((p) => p.path === folder)

          if (matched) {
            await handleSelectProject(matched.id)
          } else {
            const folderName = folder.split('\\').pop()?.split('/').pop() || 'Projeto Importado'
            const newProj = await projectService.create({
              name: folderName,
              path: folder,
              description: 'Projeto importado do sistema de arquivos'
            })
            await handleSelectProject(newProj.id)
          }
        }
      } else {
        // Web mode fallback: Open existing project or launch creation modal
        const allProjects = await projectService.list(0, 100)
        if (allProjects.projects.length > 0) {
          await handleSelectProject(allProjects.projects[0].id)
        } else {
          setIsNewModalOpen(true)
        }
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Falha ao abrir projeto', 'error')
    }
  }

  const handleSelectProject = async (id: string) => {
    await loadProject(id)
    navigate('/library')
  }

  const handleDeleteProject = async (projectId: string) => {
    if (!window.confirm('Tem certeza que deseja excluir este projeto?')) return
    try {
      await projectService.delete(projectId)
      showToast('Projeto excluído com sucesso!', 'success')
      fetchRecentProjects()
    } catch (err) {
      showToast('Falha ao excluir projeto', 'error')
    }
  }

  return (
    <div className="max-w-4xl mx-auto flex flex-col justify-center min-h-[80vh] py-12 px-4 relative select-none">
      {/* Cyber Grid Background */}
      <div className="absolute inset-0 cyber-grid-bg opacity-40 pointer-events-none" />

      {/* Main Banner / Brand Header */}
      <div className="text-center space-y-6 mb-12 relative z-10">
        <AutomaLogo className="w-24 h-24 mx-auto animate-neon-pulse rounded-xl" />
        <div className="space-y-2">
          <h1 className="text-4xl md:text-5xl font-black tracking-wider text-white">AUTOMA</h1>
          <p className="text-sm font-mono text-neon-green uppercase tracking-widest">
            Editor inteligente de vídeos em massa
          </p>
        </div>
      </div>

      {/* Action Panels */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
        {/* Core Actions */}
        <div className="md:col-span-1 space-y-4">
          <Button
            variant="primary"
            onClick={() => setIsNewModalOpen(true)}
            className="w-full py-4 text-sm font-bold flex items-center justify-center gap-2 group"
          >
            <FolderPlus className="w-5 h-5 group-hover:scale-110 transition-transform" />
            Novo Projeto
          </Button>

          <Button
            variant="cyan"
            onClick={handleOpenProject}
            className="w-full py-4 text-sm font-bold flex items-center justify-center gap-2 group"
          >
            <FolderOpen className="w-5 h-5 group-hover:scale-110 transition-transform" />
            Abrir Projeto
          </Button>

          {/* Quick links panel */}
          <Card className="p-4 bg-cyber-panel/40">
            <div className="space-y-1 font-mono text-xs">
              <button
                onClick={() => navigate('/settings')}
                className="w-full py-2 px-3 rounded text-left text-gray-400 hover:text-white hover:bg-white/5 flex items-center gap-2 transition-all"
              >
                <Settings className="w-4 h-4 text-neon-cyan" />
                Configurações
              </button>
              <a
                href="https://github.com"
                target="_blank"
                rel="noreferrer"
                className="w-full py-2 px-3 rounded text-left text-gray-400 hover:text-white hover:bg-white/5 flex items-center gap-2 transition-all block"
              >
                <HelpCircle className="w-4 h-4 text-neon-yellow" />
                Documentação & Ajuda
              </a>
            </div>
          </Card>
        </div>

        {/* Recent Projects Column */}
        <div className="md:col-span-2">
          <Card className="h-full">
            <CardHeader className="pb-2 mb-2">
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-neon-cyan" />
                Projetos Recentes
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loadingRecents ? (
                <div className="flex justify-center items-center py-12">
                  <svg
                    className="animate-spin h-5 w-5 text-neon-green"
                    viewBox="0 0 24 24"
                    fill="none"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4"
                    />
                  </svg>
                </div>
              ) : (
                <RecentProjectsList
                  projects={recentProjects}
                  onSelect={handleSelectProject}
                  onDelete={handleDeleteProject}
                />
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* New Project Registration Modal */}
      <NewProjectModal
        isOpen={isNewModalOpen}
        onClose={() => setIsNewModalOpen(false)}
        onSuccess={handleSelectProject}
      />
    </div>
  )
}
