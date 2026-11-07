import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useProject } from '../contexts/ProjectContext'
import { useToast } from '../contexts/ToastContext'
import { useImport } from '../hooks/useImport'
import { videoService } from '../services/videoService'
import { videoTemplateService } from '../services/videoTemplateService'
import { exportProfileService } from '../services/exportProfileService'
import { jobService } from '../services/jobService'
import { VideoFilters, ViewMode, SortOption } from '../components/library/VideoFilters'
import { ImportDropzone } from '../components/library/ImportDropzone'
import { VideoCard } from '../components/library/VideoCard'
import { VideoTable } from '../components/library/VideoTable'
import { Dialog } from '../components/ui/Dialog'
import { Button } from '../components/ui/Button'
import { Film, PlayCircle, Zap, Loader2, Sparkles, Eye } from 'lucide-react'
import { VideoTemplate } from '../types/videoTemplate'
import { ExportProfile } from '../types/exportProfile'

export const Library: React.FC = () => {
  const navigate = useNavigate()
  const { activeProject, videos, refreshProjectData } = useProject()
  const { showToast } = useToast()
  const { importing, progress, handleDrop, importFiles } = useImport()

  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [sortBy, setSortBy] = useState<SortOption>('date_desc')
  const [viewMode, setViewMode] = useState<ViewMode>('grid')

  // Deletion Dialog State
  const [deleteVideoId, setDeleteVideoId] = useState<string | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  // Batch Process Modal State
  const [isBatchModalOpen, setIsBatchModalOpen] = useState(false)
  const [templates, setTemplates] = useState<VideoTemplate[]>([])
  const [exportProfiles, setExportProfiles] = useState<ExportProfile[]>([])
  const [selectedTemplateId, setSelectedTemplateId] = useState('')
  const [selectedProfileId, setSelectedProfileId] = useState('')
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isPreviewing, setIsPreviewing] = useState(false)
  const [isEnqueuing, setIsEnqueuing] = useState(false)

  const handleScanVideo = async (id: string) => {
    try {
      showToast('Iniciando varredura de metadados...', 'info')
      await videoService.scanVideo(id)
      await refreshProjectData()
      showToast('Metadados do vídeo atualizados!', 'success')
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Falha ao escanear vídeo', 'error')
    }
  }

  const handleDeleteVideo = async () => {
    if (!deleteVideoId) return
    setIsDeleting(true)
    try {
      await videoService.delete(deleteVideoId)
      await refreshProjectData()
      showToast('Vídeo excluído com sucesso!', 'success')
      setDeleteVideoId(null)
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Falha ao excluir vídeo', 'error')
    } finally {
      setIsDeleting(false)
    }
  }

  const openBatchModal = async () => {
    try {
      const tRes = await videoTemplateService.list()
      const pRes = await exportProfileService.getAll()
      setTemplates(tRes.templates)
      setExportProfiles(pRes)
      if (tRes.templates.length > 0) setSelectedTemplateId(tRes.templates[0].id)
      if (pRes.length > 0) setSelectedProfileId(pRes[0].id)
      setIsBatchModalOpen(true)
    } catch (err) {
      showToast('Falha ao carregar templates ou perfis de exportação', 'error')
    }
  }

  const handlePreview = async () => {
    const sample = filteredVideos[0]
    if (!sample || !selectedTemplateId) return
    setIsPreviewing(true)
    setPreviewUrl(null)
    try {
      // Short render (first 4 s) of the first listed video with the chosen template
      const res = await jobService.preview({
        video_id: sample.id,
        template_id: selectedTemplateId,
        start_time: 0,
        end_time: 4
      })
      setPreviewUrl(res.preview_url)
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Falha ao gerar prévia', 'error')
    } finally {
      setIsPreviewing(false)
    }
  }

  const handleStartBatchProcessing = async () => {
    if (!activeProject || filteredVideos.length === 0 || !selectedTemplateId || !selectedProfileId) return
    setIsEnqueuing(true)
    try {
      let count = 0
      for (const video of filteredVideos) {
        await jobService.enqueue({
          project_id: activeProject.id,
          video_id: video.id,
          template_id: selectedTemplateId,
          export_profile_id: selectedProfileId
        })
        count++
      }
      showToast(`${count} vídeo(s) adicionados à fila de processamento!`, 'success')
      setIsBatchModalOpen(false)
      navigate('/processing')
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Erro ao iniciar processamento', 'error')
    } finally {
      setIsEnqueuing(false)
    }
  }

  // Filter and sort video list
  const filteredVideos = videos
    .filter((video) => {
      const matchSearch = video.name.toLowerCase().includes(searchQuery.toLowerCase())
      const matchStatus = statusFilter === 'all' || video.status === statusFilter
      return matchSearch && matchStatus
    })
    .sort((a, b) => {
      if (sortBy === 'date_desc') {
        return new Date(b.imported_at).getTime() - new Date(a.imported_at).getTime()
      }
      if (sortBy === 'date_asc') {
        return new Date(a.imported_at).getTime() - new Date(b.imported_at).getTime()
      }
      if (sortBy === 'name_asc') {
        return a.name.localeCompare(b.name)
      }
      if (sortBy === 'name_desc') {
        return b.name.localeCompare(a.name)
      }
      if (sortBy === 'size_desc') {
        return b.size_bytes - a.size_bytes
      }
      return 0
    })

  return (
    <div className="space-y-6 select-none">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold tracking-wider text-white">Biblioteca de Vídeos</h2>
          <p className="text-xs font-mono text-gray-500 mt-1 uppercase">
            Gerencie e organize os arquivos do projeto
          </p>
        </div>
        {filteredVideos.length > 0 && (
          <Button
            variant="primary"
            onClick={openBatchModal}
            className="flex items-center gap-2 px-4 py-2 text-sm font-bold shadow-neon-green/20 animate-pulse"
          >
            <Sparkles className="w-4 h-4 text-black fill-current" />
            <span>Processar {filteredVideos.length} Vídeo(s) em Lote</span>
          </Button>
        )}
      </div>

      {/* Dropzone for Uploads */}
      <ImportDropzone
        onDrop={handleDrop}
        importing={importing}
        progress={progress}
        onImportPaths={(paths) => importFiles(paths)}
      />

      {/* Filter and controls bar */}
      <VideoFilters
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        statusFilter={statusFilter}
        setStatusFilter={setStatusFilter}
        sortBy={sortBy}
        setSortBy={setSortBy}
        viewMode={viewMode}
        setViewMode={setViewMode}
      />

      {/* Main video presentation layout */}
      {filteredVideos.length === 0 ? (
        <div className="text-center py-16 border border-cyber-border rounded-lg bg-cyber-panel/10">
          <Film className="w-12 h-12 text-gray-700 mx-auto mb-3" />
          <p className="text-sm font-bold text-gray-400">Nenhum vídeo encontrado</p>
          <p className="text-xs text-gray-500 font-mono mt-1">
            Importe arquivos acima para começar a preencher a biblioteca
          </p>
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredVideos.map((video) => (
            <VideoCard
              key={video.id}
              video={video}
              onScan={handleScanVideo}
              onDelete={(id) => setDeleteVideoId(id)}
            />
          ))}
        </div>
      ) : (
        <VideoTable
          videos={filteredVideos}
          onScan={handleScanVideo}
          onDelete={(id) => setDeleteVideoId(id)}
        />
      )}

      {/* Confirm Deletion Dialog */}
      <Dialog
        isOpen={deleteVideoId !== null}
        onClose={() => setDeleteVideoId(null)}
        onConfirm={handleDeleteVideo}
        title="Confirmar Exclusão"
        message="Tem certeza que deseja remover este vídeo do projeto? O arquivo original no disco não será excluído, apenas a cópia interna do projeto."
        confirmText="Excluir"
        variant="danger"
        isLoading={isDeleting}
      />

      {/* Batch Processing Modal */}
      {isBatchModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-cyber-panel border border-cyber-border rounded-xl max-w-lg w-full p-6 space-y-6 shadow-2xl">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Zap className="w-5 h-5 text-neon-green" />
                Processamento Automático em Lote
              </h3>
              <p className="text-xs font-mono text-gray-400 mt-1">
                Aplique o mesmo Template e Perfil de Exportação para os {filteredVideos.length} vídeos da lista.
              </p>
            </div>

            <div className="space-y-4 font-mono text-xs">
              <div>
                <label className="block text-gray-300 mb-1.5 font-bold uppercase">
                  1. Selecione o Template
                </label>
                {templates.length === 0 ? (
                  <p className="text-neon-pink">Nenhum template encontrado. Crie um na aba Templates primeiro!</p>
                ) : (
                  <select
                    value={selectedTemplateId}
                    onChange={(e) => setSelectedTemplateId(e.target.value)}
                    className="w-full bg-black/60 border border-cyber-border rounded p-2.5 text-white focus:border-neon-green outline-none"
                  >
                    {templates.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.name}
                      </option>
                    ))}
                  </select>
                )}
              </div>

              <div>
                <label className="block text-gray-300 mb-1.5 font-bold uppercase">
                  2. Selecione o Perfil de Exportação
                </label>
                {exportProfiles.length === 0 ? (
                  <p className="text-neon-pink">Nenhum perfil de exportação encontrado.</p>
                ) : (
                  <select
                    value={selectedProfileId}
                    onChange={(e) => setSelectedProfileId(e.target.value)}
                    className="w-full bg-black/60 border border-cyber-border rounded p-2.5 text-white focus:border-neon-green outline-none"
                  >
                    {exportProfiles.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name} ({p.resolution}, {p.fps}fps)
                      </option>
                    ))}
                  </select>
                )}
              </div>
            </div>

            {(previewUrl || isPreviewing) && (
              <div className="flex justify-center">
                {isPreviewing ? (
                  <p className="text-xs font-mono text-gray-400 flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" /> Gerando prévia...
                  </p>
                ) : (
                  <video
                    key={previewUrl ?? ''}
                    src={previewUrl ?? undefined}
                    controls
                    autoPlay
                    loop
                    className="max-h-80 rounded border border-cyber-border"
                  />
                )}
              </div>
            )}

            <div className="flex justify-end gap-3 pt-4 border-t border-cyber-border/40">
              <Button
                variant="secondary"
                onClick={handlePreview}
                disabled={isEnqueuing || isPreviewing || !selectedTemplateId || filteredVideos.length === 0}
                className="flex items-center gap-2"
              >
                <Eye className="w-4 h-4" />
                Prévia
              </Button>
              <Button
                variant="secondary"
                onClick={() => {
                  setPreviewUrl(null)
                  setIsBatchModalOpen(false)
                }}
                disabled={isEnqueuing}
              >
                Cancelar
              </Button>
              <Button
                variant="primary"
                onClick={handleStartBatchProcessing}
                disabled={isEnqueuing || !selectedTemplateId || !selectedProfileId}
                className="flex items-center gap-2"
              >
                {isEnqueuing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Enfileirando...
                  </>
                ) : (
                  <>
                    <PlayCircle className="w-4 h-4 fill-current" />
                    Iniciar Renderização ({filteredVideos.length})
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
