import React from 'react'
import { Cpu, HardDrive, Shield } from 'lucide-react'
import { useProject } from '../../contexts/ProjectContext'
import { formatBytes } from '../../utils/format'

export const Navbar: React.FC = () => {
  const { activeProject, totalVideos, totalBytes } = useProject()

  return (
    <header className="h-16 cyber-panel border-b border-cyber-border px-8 flex items-center justify-between shrink-0 select-none">
      {/* Title / Breadcrumb */}
      <div className="flex items-center gap-3">
        {activeProject ? (
          <>
            <span className="text-gray-500 font-mono text-xs">
              / projetos / {activeProject.category || 'geral'}
            </span>
            <span className="text-gray-300">/</span>
            <span className="font-bold text-white text-sm tracking-wider">
              {activeProject.name}
            </span>
          </>
        ) : (
          <span className="font-semibold text-gray-400 text-sm tracking-wider">
            AUTOMA Dashboard
          </span>
        )}
      </div>

      {/* Header Metrics / Telemetry Quick Stats */}
      <div className="flex items-center gap-6">
        {activeProject && (
          <div className="flex items-center gap-6 text-xs font-mono text-gray-400 border-r border-cyber-border pr-6">
            <div className="flex items-center gap-2">
              <HardDrive className="w-4 h-4 text-neon-cyan" />
              <span>
                Vídeos: <strong className="text-white">{totalVideos}</strong>
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-neon-yellow" />
              <span>
                Espaço: <strong className="text-white">{formatBytes(totalBytes)}</strong>
              </span>
            </div>
          </div>
        )}

        {/* Status Indicators */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 bg-cyber-bg/60 border border-cyber-border px-3 py-1 rounded-md text-[10px] font-mono text-neon-green">
            <Cpu className="w-3.5 h-3.5" />
            <span>API: ONLINE</span>
          </div>
        </div>
      </div>
    </header>
  )
}
