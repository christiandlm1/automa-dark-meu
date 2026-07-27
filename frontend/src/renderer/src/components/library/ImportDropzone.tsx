import React, { useRef, useState } from 'react'
import { UploadCloud, Folder } from 'lucide-react'
import { ProgressBar } from '../ui/ProgressBar'

interface ImportDropzoneProps {
  onDrop: (e: React.DragEvent<HTMLDivElement>) => void
  importing: boolean
  progress: number
  onImportPaths: (input: FileList | File[] | string[]) => void
}

export const ImportDropzone: React.FC<ImportDropzoneProps> = ({
  onDrop,
  importing,
  progress,
  onImportPaths
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const folderInputRef = useRef<HTMLInputElement>(null)
  const [isDragOver, setIsDragOver] = useState(false)

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)
  }

  const handleDropInternal = (e: React.DragEvent<HTMLDivElement>) => {
    setIsDragOver(false)
    onDrop(e)
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onImportPaths(e.target.files)
    }
  }

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDropInternal}
      className={`border-2 border-dashed rounded-lg p-10 flex flex-col items-center justify-center text-center transition-all duration-300 relative ${
        isDragOver
          ? 'border-neon-green bg-neon-green/5 shadow-[0_0_15px_rgba(57,255,20,0.1)]'
          : 'border-cyber-border hover:border-gray-600 bg-cyber-panel/20'
      }`}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        multiple
        className="hidden"
      />
      <input
        type="file"
        ref={folderInputRef}
        onChange={handleFileChange}
        {...({ webkitdirectory: '', directory: '' } as any)}
        className="hidden"
      />

      {importing ? (
        <div className="space-y-4 w-full max-w-xs select-none">
          <UploadCloud className="w-10 h-10 text-neon-green animate-bounce mx-auto" />
          <span className="text-xs font-mono font-bold text-gray-400 block uppercase">
            Processando Vídeos do Projeto...
          </span>
          <ProgressBar value={progress} color="green" showText />
        </div>
      ) : (
        <div className="space-y-3 cursor-pointer select-none">
          <UploadCloud className="w-12 h-12 text-gray-600 group-hover:text-gray-400 mx-auto" />
          <div>
            <p className="text-sm font-bold text-white">
              Arraste e solte vídeos ou pastas inteiras aqui
            </p>
            <p className="text-xs text-gray-500 font-mono mt-1">
              Formatos aceitos: MP4, MOV, AVI, MKV, WEBM
            </p>
          </div>
          <div className="flex justify-center gap-3 pt-2">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-3 py-1.5 bg-cyber-surface border border-cyber-border rounded text-xs text-gray-300 hover:text-white hover:border-gray-500 transition-colors flex items-center gap-1.5"
            >
              <UploadCloud className="w-3.5 h-3.5" />
              Importar Arquivos
            </button>
            <button
              onClick={() => folderInputRef.current?.click()}
              className="px-3 py-1.5 bg-cyber-surface border border-cyber-border rounded text-xs text-gray-300 hover:text-white hover:border-gray-500 transition-colors flex items-center gap-1.5"
            >
              <Folder className="w-3.5 h-3.5" />
              Importar Pastas
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
