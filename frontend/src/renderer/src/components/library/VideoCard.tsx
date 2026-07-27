import React from 'react'
import { Video } from '../../types/video'
import { Card, CardContent } from '../ui/Card'
import { Play, FileVideo, Calendar, HardDrive, Trash2 } from 'lucide-react'
import { formatBytes, formatDuration, formatDate, formatFPS } from '../../utils/format'

interface VideoCardProps {
  video: Video
  onDelete: (id: string) => void
  onScan: (id: string) => void
}

export const VideoCard: React.FC<VideoCardProps> = ({ video, onDelete, onScan }) => {
  const isPending = video.status === 'pending'

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

  const thumbnailUrl = video.thumbnail_path
    ? `http://127.0.0.1:8420/thumbnails/${video.thumbnail_path.split('\\').pop()?.split('/').pop()}`
    : null

  return (
    <Card className="cyber-panel-interactive p-0 flex flex-col group overflow-hidden h-full">
      <CardContent className="flex flex-col h-full">
        {/* Thumbnail Preview Area */}
        <div className="relative aspect-video w-full bg-black/60 flex items-center justify-center overflow-hidden border-b border-cyber-border">
          {thumbnailUrl ? (
            <img
              src={thumbnailUrl}
              alt={video.name}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              onError={(e) => {
                // Fallback on image error
                ;(e.target as HTMLElement).style.display = 'none'
              }}
            />
          ) : (
            <FileVideo className="w-10 h-10 text-gray-700" />
          )}

          {/* Quick stats floating badges */}
          {video.duration !== undefined && (
            <span className="absolute bottom-2 right-2 bg-black/80 px-2 py-0.5 rounded text-[10px] font-mono text-white font-bold tracking-wider">
              {formatDuration(video.duration)}
            </span>
          )}

          {/* Overlay actions on hover */}
          <div className="absolute inset-0 bg-black/65 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3">
            {isPending && (
              <button
                onClick={() => onScan(video.id)}
                className="p-2.5 rounded-full bg-neon-green hover:bg-neon-green/80 text-black shadow-lg hover:shadow-neon-green/30 transition-all"
                title="Escanear vídeo"
              >
                <Play className="w-4 h-4 fill-current" />
              </button>
            )}
            <button
              onClick={() => onDelete(video.id)}
              className="p-2.5 rounded-full bg-neon-pink/20 hover:bg-neon-pink border border-neon-pink/40 hover:border-neon-pink text-neon-pink hover:text-black shadow-lg transition-all"
              title="Excluir vídeo"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Video Information Body */}
        <div className="p-4 flex-1 flex flex-col justify-between">
          <div className="space-y-2">
            {/* Title / Name */}
            <h4
              className="text-xs font-bold text-white tracking-wide truncate group-hover:text-neon-green transition-colors"
              title={video.name}
            >
              {video.name}
            </h4>

            {/* Tech metadata grids */}
            <div className="grid grid-cols-2 gap-x-2 gap-y-1.5 text-[10px] font-mono text-gray-400">
              <span className="truncate">
                Res: <strong className="text-gray-200">{video.resolution || '-'}</strong>
              </span>
              <span className="truncate">
                FPS: <strong className="text-gray-200">{formatFPS(video.fps)}</strong>
              </span>
              <span className="truncate">
                Codec: <strong className="text-gray-200 uppercase">{video.codec || '-'}</strong>
              </span>
              <span className="truncate flex items-center gap-1">
                <HardDrive className="w-3.5 h-3.5" />
                <strong className="text-gray-200">{formatBytes(video.size_bytes)}</strong>
              </span>
            </div>
          </div>

          {/* Footer details */}
          <div className="mt-4 pt-3 border-t border-cyber-border/40 flex items-center justify-between">
            {/* Date imported */}
            <div className="flex items-center gap-1 text-[9px] font-mono text-gray-500">
              <Calendar className="w-3 h-3" />
              <span>{formatDate(video.imported_at)}</span>
            </div>

            {/* Status Badge */}
            <span
              className={`px-2 py-0.5 rounded border text-[9px] font-mono font-bold uppercase tracking-wider ${
                statusBadges[video.status]
              }`}
            >
              {statusLabels[video.status]}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
