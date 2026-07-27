/**
 * Format bytes to a human-readable string (KB, MB, GB, TB).
 */
export function formatBytes(bytes: number, decimals = 2): string {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']

  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

/**
 * Format video duration in seconds to a HH:MM:SS string.
 */
export function formatDuration(seconds: number | undefined): string {
  if (seconds === undefined || isNaN(seconds)) return '00:00'

  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)

  const parts: string[] = []
  if (h > 0) {
    parts.push(h.toString().padStart(2, '0'))
  }
  parts.push(m.toString().padStart(2, '0'))
  parts.push(s.toString().padStart(2, '0'))

  return parts.join(':')
}

/**
 * Format a date string to a localized short string.
 */
export function formatDate(dateString: string): string {
  if (!dateString) return ''
  try {
    const d = new Date(dateString)
    return d.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateString
  }
}

/**
 * Format FPS to a human-readable label.
 */
export function formatFPS(fps: number | undefined): string {
  if (fps === undefined || isNaN(fps)) return '-'
  return `${Math.round(fps)} FPS`
}

/**
 * Format resolution width and height to "WxH".
 */
export function formatResolution(width?: number, height?: number): string {
  if (!width || !height) return '-'
  return `${width}x${height}`
}
