import React from 'react'
import { LayoutGrid, List, Search } from 'lucide-react'

export type ViewMode = 'grid' | 'list'
export type SortOption = 'date_desc' | 'date_asc' | 'name_asc' | 'name_desc' | 'size_desc'

interface VideoFiltersProps {
  searchQuery: string
  setSearchQuery: (q: string) => void
  statusFilter: string
  setStatusFilter: (s: string) => void
  sortBy: SortOption
  setSortBy: (opt: SortOption) => void
  viewMode: ViewMode
  setViewMode: (m: ViewMode) => void
}

export const VideoFilters: React.FC<VideoFiltersProps> = ({
  searchQuery,
  setSearchQuery,
  statusFilter,
  setStatusFilter,
  sortBy,
  setSortBy,
  viewMode,
  setViewMode
}) => {
  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-cyber-panel/60 border border-cyber-border p-4 rounded-lg select-none">
      {/* Search Input */}
      <div className="relative flex-1 max-w-md">
        <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500">
          <Search className="w-4 h-4" />
        </span>
        <input
          type="text"
          placeholder="Pesquisar por nome do vídeo..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full bg-cyber-bg border border-cyber-border focus:border-neon-green/60 focus:ring-1 focus:ring-neon-green/40 rounded pl-10 pr-4 py-2 text-sm text-white placeholder-gray-500 outline-none transition-all"
        />
      </div>

      {/* Select Filters & Ordering */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-cyber-bg border border-cyber-border focus:border-neon-green/60 text-xs text-gray-300 rounded px-3 py-2 outline-none cursor-pointer"
        >
          <option value="all">Todos Status</option>
          <option value="scanned">Escaneados</option>
          <option value="pending">Pendentes</option>
          <option value="error">Erros</option>
        </select>

        {/* Ordering */}
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as SortOption)}
          className="bg-cyber-bg border border-cyber-border focus:border-neon-green/60 text-xs text-gray-300 rounded px-3 py-2 outline-none cursor-pointer"
        >
          <option value="date_desc">Mais Recentes</option>
          <option value="date_asc">Mais Antigos</option>
          <option value="name_asc">Nome (A-Z)</option>
          <option value="name_desc">Nome (Z-A)</option>
          <option value="size_desc">Tamanho (Maior)</option>
        </select>

        {/* View Mode Toggle */}
        <div className="flex border border-cyber-border rounded overflow-hidden">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 transition-colors ${
              viewMode === 'grid'
                ? 'bg-neon-green text-black'
                : 'bg-cyber-bg text-gray-400 hover:text-white'
            }`}
            title="Visualização em Grade"
          >
            <LayoutGrid className="w-4 h-4" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 transition-colors ${
              viewMode === 'list'
                ? 'bg-neon-green text-black'
                : 'bg-cyber-bg text-gray-400 hover:text-white'
            }`}
            title="Visualização em Lista"
          >
            <List className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
