const ALLOWED_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.webm']

/**
 * Check if a filename corresponds to a valid video type.
 */
export function isValidVideoExtension(filename: string): boolean {
  const lower = filename.toLowerCase()
  return ALLOWED_EXTENSIONS.some((ext) => lower.endsWith(ext))
}

/**
 * Validate project name (alphanumeric and spaces only).
 */
export function isValidProjectName(name: string): boolean {
  const trimmed = name.trim()
  if (trimmed.length < 2 || trimmed.length > 50) return false
  return /^[a-zA-Z0-9_\s\-]+$/.test(trimmed)
}
