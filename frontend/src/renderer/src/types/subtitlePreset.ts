export type SubtitleFont =
  'Arial' | 'Roboto' | 'Montserrat' | 'Bebas Neue' | 'Anton' | 'Oswald' | 'Impact'

export interface SubtitlePreset {
  id: string
  name: string
  font: SubtitleFont
  size: number
  primary_color: string
  secondary_color: string
  background_color: string
  max_lines: number
  word_wrap: number
  uppercase: boolean
  alignment: 'left' | 'center' | 'right'
  created_at?: string
  updated_at?: string
}

export type SubtitlePresetCreate = Omit<SubtitlePreset, 'id' | 'created_at' | 'updated_at'>
export type SubtitlePresetUpdate = Partial<SubtitlePresetCreate>
