import React from 'react'
import { Video } from '../../types/video'
import { TableCell } from '../ui/Table'
import { Play, Trash2, FileVideo } from 'lucide-react'
import { formatBytes, formatDuration, formatDate, formatFPS } from '../../utils/format'
import { TableVirtuoso } from 'react-virtuoso'

interface VideoTableProps {
  videos: Video[]
  onDelete: (id: string) => void
  onScan: (id: string) => void
}

export const VideoTable: React.FC<VideoTableProps> = ({ videos, onDelete, onScan }) => {
  const headers = [
    'Miniatura',
    'Nome',
    'Duração',
    'Resolução',
    'FPS',
    'Codec',
    'Tamanho',
    'Importado Em',
    'Status',
    'Ações'
  ]

  const statusBadges = {
    scanned: 'bg-neon-green/10 border-neon-green/30 text-neon-green',
    pending: 'bg-neon-cyan/10 border-neon-cyan/30 text-neon-cyan',
    error: 'bg-neon-pink/10 border-neon-pink/30 text-neon-pink'
  }

  const statusLabels = {
    scanned: 'Escaneado',
    pending: 'Pendente',
    error: 'Erro'
  }

  return (
    <div className="h-full min-h-[400px]">
      <TableVirtuoso
        data={videos}
        className="h-full w-full custom-scrollbar bg-cyber-panel/40 border border-cyber-border rounded-lg"
        components={{
          Table: (props) => (
            <table className="w-full text-left border-collapse text-sm" {...props} />
          ),
          TableHead: React.forwardRef((props, ref) => (
            <thead
              className="bg-cyber-bg/60 select-none border-b border-cyber-border"
              {...props}
              ref={ref}
            />
          )),
          TableRow: (props) => (
            <tr
              className="hover:bg-cyber-surface/30 transition-colors duration-150 border-b border-cyber-border/40 group"
              {...props}
            />
          )
        }}
        fixedHeaderContent={() => (
          <tr>
            {headers.map((h) => (
              <th
                key={h}
                className="py-3.5 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono bg-cyber-bg"
              >
                {h}
              </th>
            ))}
          </tr>
        )}
        itemContent={(_, video) => {
          const isPending = video.status === 'pending'
          const thumbnailUrl = video.thumbnail_path
            ? `http://127.0.0.1:8420/thumbnails/${video.thumbnail_path.split('\\').pop()?.split('/').pop()}`
            : null

          return (
            <>
              {/* Thumbnail */}
              <TableCell className="w-20">
                <div className="w-16 aspect-video bg-black/60 rounded border border-cyber-border overflow-hidden flex items-center justify-center shrink-0">
                  {thumbnailUrl ? (
                    <img
                      src={thumbnailUrl}
                      alt={video.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <FileVideo className="w-5 h-5 text-gray-700" />
                  )}
                </div>
              </TableCell>

              {/* Name */}
              <TableCell className="max-w-[200px] truncate font-bold text-white" title={video.name}>
                {video.name}
              </TableCell>

              {/* Duration */}
              <TableCell className="font-mono text-xs">{formatDuration(video.duration)}</TableCell>

              {/* Resolution */}
              <TableCell className="font-mono text-xs">{video.resolution || '-'}</TableCell>

              {/* FPS */}
              <TableCell className="font-mono text-xs">{formatFPS(video.fps)}</TableCell>

              {/* Codec */}
              <TableCell className="font-mono text-xs uppercase text-gray-400">
                {video.codec || '-'}
              </TableCell>

              {/* Size */}
              <TableCell className="font-mono text-xs">{formatBytes(video.size_bytes)}</TableCell>

              {/* Import Date */}
              <TableCell className="font-mono text-[10px] text-gray-400">
                {formatDate(video.imported_at)}
              </TableCell>

              {/* Status */}
              <TableCell>
                <span
                  className={`px-2 py-0.5 rounded border text-[10px] font-mono font-bold uppercase tracking-wider ${
                    statusBadges[video.status]
                  }`}
                >
                  {statusLabels[video.status]}
                </span>
              </TableCell>

              {/* Actions */}
              <TableCell>
                <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  {isPending && (
                    <button
                      onClick={() => onScan(video.id)}
                      className="p-1.5 rounded bg-neon-green/10 border border-neon-green/30 hover:bg-neon-green hover:text-black text-neon-green transition-all"
                      title="Escanear vídeo"
                    >
                      <Play className="w-3.5 h-3.5 fill-current" />
                    </button>
                  )}
                  <button
                    onClick={() => onDelete(video.id)}
                    className="p-1.5 rounded bg-neon-pink/10 border border-neon-pink/30 hover:bg-neon-pink hover:text-black text-neon-pink transition-all"
                    title="Excluir vídeo"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </TableCell>
            </>
          )
        }}
      />
    </div>
  )
}
