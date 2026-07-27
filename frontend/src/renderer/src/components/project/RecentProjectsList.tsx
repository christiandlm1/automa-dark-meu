import React from 'react'
import { Folder, Clock, ArrowRight, Trash2 } from 'lucide-react'
import { RecentProject } from '../../types/project'
import { Card, CardContent } from '../ui/Card'
import { formatDate } from '../../utils/format'

interface RecentProjectsListProps {
  projects: RecentProject[]
  onSelect: (projectId: string) => void
  onDelete?: (projectId: string) => void
}

export const RecentProjectsList: React.FC<RecentProjectsListProps> = ({
  projects,
  onSelect,
  onDelete
}) => {
  if (projects.length === 0) {
    return (
      <div className="text-center py-8 border border-dashed border-cyber-border rounded-lg bg-cyber-panel/20 select-none">
        <Folder className="w-8 h-8 text-gray-600 mx-auto mb-2" />
        <span className="text-xs font-mono text-gray-500">Nenhum projeto recente encontrado</span>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {projects.map((project) => (
        <Card
          key={project.id}
          hoverable
          onClick={() => onSelect(project.project_id)}
          className="cyber-panel-interactive p-4 flex items-center justify-between group"
        >
          <CardContent className="flex items-center gap-4 w-full justify-between">
            <div className="flex items-center gap-3 truncate min-w-0 pr-4">
              <div className="p-2 bg-cyber-surface border border-cyber-border rounded-lg text-neon-cyan shrink-0">
                <Folder className="w-5 h-5" />
              </div>
              <div className="truncate">
                <span className="text-sm font-bold text-white block group-hover:text-neon-green transition-colors truncate">
                  {project.name}
                </span>
                <span
                  className="text-[10px] text-gray-500 font-mono block truncate"
                  title={project.path}
                >
                  {project.path}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-4 shrink-0 font-mono text-[10px] text-gray-400">
              <div className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-gray-500" />
                <span>Aberto: {formatDate(project.last_opened_at)}</span>
              </div>
              {onDelete && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    onDelete(project.project_id)
                  }}
                  className="p-1.5 rounded hover:bg-neon-pink/20 text-gray-500 hover:text-neon-pink transition-colors"
                  title="Excluir Projeto"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
              <ArrowRight className="w-4 h-4 text-gray-600 group-hover:text-neon-green group-hover:translate-x-1 transition-all" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
