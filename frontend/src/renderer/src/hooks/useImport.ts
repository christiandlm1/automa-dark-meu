import { useState, useCallback } from 'react'
import { useProject } from '../contexts/ProjectContext'
import { useToast } from '../contexts/ToastContext'
import { videoService } from '../services/videoService'

const ALLOWED_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.webm']

export function useImport() {
  const { activeProject, refreshProjectData } = useProject()
  const { showToast } = useToast()
  const [importing, setImporting] = useState(false)
  const [progress, setProgress] = useState(0)

  const processFileSelection = useCallback(
    async (fileInput: FileList | File[] | string[]) => {
      if (!activeProject) {
        showToast('Selecione ou crie um projeto primeiro', 'warning')
        return
      }

      setImporting(true)
      setProgress(10)

      try {
        // If string array (paths)
        if (
          Array.isArray(fileInput) &&
          fileInput.length > 0 &&
          typeof fileInput[0] === 'string'
        ) {
          showToast(`Importando ${fileInput.length} arquivo(s)...`, 'info')
          setProgress(40)
          await videoService.importVideos({
            project_id: activeProject.id,
            file_paths: fileInput as string[]
          })
        } else {
          // FileList or File[]
          const files = Array.from(fileInput as FileList)
          const validFiles = files.filter((f) => {
            const ext = f.name.toLowerCase().substring(f.name.lastIndexOf('.'))
            return ALLOWED_EXTENSIONS.includes(ext)
          })

          if (validFiles.length === 0) {
            showToast('Nenhum arquivo de vídeo válido encontrado (MP4, MOV, AVI, MKV, WEBM)', 'warning')
            return
          }

          // Check if file.path is available (Electron desktop mode)
          const hasNativePaths = validFiles.every((f) => (f as any).path)

          if (hasNativePaths) {
            const paths = validFiles.map((f) => (f as any).path)
            showToast(`Importando ${paths.length} vídeo(s)...`, 'info')
            setProgress(40)
            await videoService.importVideos({
              project_id: activeProject.id,
              file_paths: paths
            })
          } else {
            // Web Browser mode: Upload actual file bytes via multipart form data
            showToast(`Enviando ${validFiles.length} vídeo(s) para o servidor...`, 'info')
            setProgress(40)
            await videoService.uploadFiles(activeProject.id, validFiles)
          }
        }

        setProgress(80)
        await refreshProjectData()
        setProgress(100)
        showToast('Vídeos importados com sucesso!', 'success')

        // Trigger background scan for thumbnails & metadata
        videoService
          .scanPending(activeProject.id)
          .then(() => refreshProjectData())
          .catch((e) => console.error('Auto-scan failed:', e))
      } catch (err) {
        showToast(err instanceof Error ? err.message : 'Erro ao importar vídeos', 'error')
      } finally {
        setTimeout(() => {
          setImporting(false)
          setProgress(0)
        }, 500)
      }
    },
    [activeProject, refreshProjectData, showToast]
  )

  const importFiles = useCallback(
    async (input: FileList | File[] | string[]) => {
      await processFileSelection(input)
    },
    [processFileSelection]
  )

  const handleDrop = useCallback(
    async (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      e.stopPropagation()

      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        await processFileSelection(e.dataTransfer.files)
      }
    },
    [processFileSelection]
  )

  return {
    importing,
    progress,
    importFiles,
    handleDrop
  }
}
