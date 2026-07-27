import React from 'react'
import { NavLink } from 'react-router-dom'
import {
  Home,
  LayoutDashboard,
  FolderKanban,
  Settings,
  Terminal,
  XCircle,
  Sliders,
  PlayCircle,
  Download,
  Type
} from 'lucide-react'
import { useProject } from '../../contexts/ProjectContext'
import { AutomaLogo } from '../../icons/AutomaLogo'

export const Sidebar: React.FC = () => {
  const { activeProject, closeProject } = useProject()

  const navItems = [
    { to: '/', label: 'Home', icon: Home, disabled: false },
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, disabled: !activeProject },
    { to: '/library', label: 'Projetos e Mídia', icon: FolderKanban, disabled: !activeProject },
    { to: '/assets', label: 'Biblioteca de Assets', icon: FolderKanban, disabled: false },
    { to: '/templates', label: 'Templates', icon: Sliders, disabled: false },
    { to: '/subtitle-presets', label: 'Legendas', icon: Type, disabled: false },
    { to: '/export-profiles', label: 'Exportação', icon: Download, disabled: false },
    { to: '/processing', label: 'PROCESSAMENTO', icon: PlayCircle, disabled: !activeProject },
    { to: '/settings', label: 'Configurações', icon: Settings, disabled: false },
    { to: '/logs', label: 'Logs', icon: Terminal, disabled: !activeProject }
  ]

  return (
    <aside className="w-64 h-screen cyber-panel border-r border-cyber-border flex flex-col justify-between shrink-0 select-none z-10">
      {/* Brand & Logo */}
      <div className="p-6 border-b border-cyber-border flex items-center gap-3">
        <AutomaLogo className="w-8 h-8" />
        <div className="flex flex-col">
          <span className="font-bold tracking-wider text-white">AUTOMA</span>
          <span className="text-[10px] text-neon-green tracking-widest uppercase">
            Video Manager
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon

          if (item.disabled) {
            return (
              <div
                key={item.to}
                className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-600 cursor-not-allowed text-sm"
                title="Abra ou crie um projeto primeiro"
              >
                <Icon className="w-5 h-5 shrink-0" />
                <span>{item.label}</span>
              </div>
            )
          }

          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-all duration-200 ${
                  isActive
                    ? 'glow-btn-green text-black font-semibold'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`
              }
            >
              <Icon className="w-5 h-5 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>

      {/* Footer Info / Active Project */}
      <div className="p-4 border-t border-cyber-border space-y-3 bg-cyber-bg/40">
        {activeProject ? (
          <div className="space-y-2">
            <div className="flex items-start justify-between">
              <div className="truncate pr-2">
                <span className="text-[10px] uppercase text-gray-500 block font-mono">
                  Projeto Ativo
                </span>
                <span
                  className="text-sm font-semibold text-white truncate block"
                  title={activeProject.name}
                >
                  {activeProject.name}
                </span>
              </div>
              <button
                onClick={closeProject}
                className="text-gray-500 hover:text-neon-pink transition-colors p-1"
                title="Fechar Projeto"
              >
                <XCircle className="w-4 h-4" />
              </button>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-neon-green animate-pulse" />
              <span className="text-[10px] text-neon-green uppercase font-mono tracking-wider">
                ONLINE
              </span>
            </div>
          </div>
        ) : (
          <div className="text-center py-2">
            <span className="text-xs text-gray-500 font-mono">Nenhum projeto aberto</span>
          </div>
        )}
        <div className="text-[10px] text-gray-600 text-center font-mono pt-1">v1.0.0 — Mod. 01</div>
      </div>
    </aside>
  )
}
