import React, { useState, useEffect } from 'react'
import { Plus, Trash2, Edit, Check, X, Type } from 'lucide-react'
import { subtitlePresetService } from '../services/subtitlePresetService'
import { SubtitlePreset, SubtitlePresetCreate, SubtitleFont } from '../types/subtitlePreset'

const FONTS: SubtitleFont[] = [
  'Arial',
  'Roboto',
  'Montserrat',
  'Bebas Neue',
  'Anton',
  'Oswald',
  'Impact'
]

export const SubtitlePresets: React.FC = () => {
  const [presets, setPresets] = useState<SubtitlePreset[]>([])
  const [editingId, setEditingId] = useState<string | null>(null)

  const [formData, setFormData] = useState<Partial<SubtitlePreset>>({
    name: '',
    font: 'Roboto',
    size: 48,
    primary_color: '#FFFFFF',
    secondary_color: '#000000',
    background_color: '#00000080',
    max_lines: 2,
    word_wrap: 40,
    uppercase: false,
    alignment: 'center'
  })

  useEffect(() => {
    loadPresets()
  }, [])

  const loadPresets = async () => {
    const data = await subtitlePresetService.list()
    setPresets(data)
  }

  const handleSave = async () => {
    if (!formData.name) return

    if (editingId) {
      await subtitlePresetService.update(editingId, formData as Partial<SubtitlePresetCreate>)
    } else {
      await subtitlePresetService.create(formData as SubtitlePresetCreate)
    }

    setEditingId(null)
    resetForm()
    loadPresets()
  }

  const handleDelete = async (id: string) => {
    if (confirm('Tem certeza que deseja excluir este preset de legenda?')) {
      await subtitlePresetService.delete(id)
      loadPresets()
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      font: 'Roboto',
      size: 48,
      primary_color: '#FFFFFF',
      secondary_color: '#000000',
      background_color: '#00000080',
      max_lines: 2,
      word_wrap: 40,
      uppercase: false,
      alignment: 'center'
    })
  }

  const startEdit = (preset: SubtitlePreset) => {
    setEditingId(preset.id)
    setFormData(preset)
  }

  // Preview helper logic
  const getPreviewStyle = (): React.CSSProperties => {
    return {
      fontFamily: formData.font,
      fontSize: `${formData.size}px`,
      color: formData.primary_color,
      backgroundColor: formData.background_color,
      textShadow: `2px 2px 0px ${formData.secondary_color}, -2px -2px 0px ${formData.secondary_color}, 2px -2px 0px ${formData.secondary_color}, -2px 2px 0px ${formData.secondary_color}`,
      textAlign: formData.alignment as any,
      textTransform: formData.uppercase ? 'uppercase' : 'none',
      padding: '8px 16px',
      borderRadius: '4px',
      display: 'inline-block',
      maxWidth: '100%',
      wordWrap: 'break-word',
      lineHeight: '1.2'
    }
  }

  return (
    <div className="space-y-6 h-full flex flex-col">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Type className="w-6 h-6 text-neon-blue" />
          Presets de Legenda
        </h1>
        <button
          onClick={() => {
            setEditingId(null)
            resetForm()
          }}
          className="btn-primary"
        >
          <Plus className="w-4 h-4 mr-2" />
          Novo Preset
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 min-h-0">
        {/* Editor Form */}
        <div className="cyber-panel p-6 overflow-y-auto">
          <h2 className="text-xl font-bold text-neon-blue mb-4">
            {editingId ? 'Editar Preset' : 'Criar Novo Preset'}
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Nome do Preset</label>
              <input
                type="text"
                className="input-cyber w-full"
                value={formData.name || ''}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Ex: Legenda Principal"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Fonte</label>
                <select
                  className="input-cyber w-full"
                  value={formData.font || 'Roboto'}
                  onChange={(e) =>
                    setFormData({ ...formData, font: e.target.value as SubtitleFont })
                  }
                >
                  {FONTS.map((f) => (
                    <option key={f} value={f}>
                      {f}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Tamanho (px)</label>
                <input
                  type="number"
                  className="input-cyber w-full"
                  value={formData.size || 48}
                  onChange={(e) => setFormData({ ...formData, size: Number(e.target.value) })}
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Cor Primária</label>
                <input
                  type="color"
                  className="w-full h-10 bg-cyber-bg border border-cyber-border rounded"
                  value={formData.primary_color || '#FFFFFF'}
                  onChange={(e) => setFormData({ ...formData, primary_color: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Cor Secundária
                </label>
                <input
                  type="color"
                  className="w-full h-10 bg-cyber-bg border border-cyber-border rounded"
                  value={formData.secondary_color || '#000000'}
                  onChange={(e) => setFormData({ ...formData, secondary_color: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Fundo (Hex/RGBA)
                </label>
                <input
                  type="text"
                  className="input-cyber w-full"
                  value={formData.background_color || '#00000080'}
                  onChange={(e) => setFormData({ ...formData, background_color: e.target.value })}
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Max Linhas</label>
                <input
                  type="number"
                  className="input-cyber w-full"
                  value={formData.max_lines || 2}
                  onChange={(e) => setFormData({ ...formData, max_lines: Number(e.target.value) })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Qtd Palavras/Linha
                </label>
                <input
                  type="number"
                  className="input-cyber w-full"
                  value={formData.word_wrap || 40}
                  onChange={(e) => setFormData({ ...formData, word_wrap: Number(e.target.value) })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Alinhamento</label>
                <select
                  className="input-cyber w-full"
                  value={formData.alignment || 'center'}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      alignment: e.target.value as 'left' | 'center' | 'right'
                    })
                  }
                >
                  <option value="left">Esquerda</option>
                  <option value="center">Centro</option>
                  <option value="right">Direita</option>
                </select>
              </div>
            </div>

            <div>
              <label className="flex items-center space-x-2 text-sm font-medium text-gray-300 cursor-pointer">
                <input
                  type="checkbox"
                  className="form-checkbox text-neon-blue bg-cyber-bg border-cyber-border rounded focus:ring-neon-blue"
                  checked={formData.uppercase || false}
                  onChange={(e) => setFormData({ ...formData, uppercase: e.target.checked })}
                />
                <span>Forçar Maiúsculas (Uppercase)</span>
              </label>
            </div>

            <div className="pt-4 flex justify-end gap-2 border-t border-cyber-border mt-6">
              {editingId && (
                <button onClick={resetForm} className="btn-secondary">
                  <X className="w-4 h-4 mr-2" /> Cancelar
                </button>
              )}
              <button onClick={handleSave} className="btn-primary" disabled={!formData.name}>
                <Check className="w-4 h-4 mr-2" /> Salvar Preset
              </button>
            </div>
          </div>

          {/* Live Preview */}
          <div className="mt-8 border-t border-cyber-border pt-6">
            <h3 className="text-lg font-bold text-white mb-4">Preview</h3>
            <div
              className="relative w-full h-48 bg-gray-900 rounded-lg overflow-hidden flex items-end justify-center pb-4 pattern-grid-lg"
              style={{
                backgroundImage:
                  'linear-gradient(#333 1px, transparent 1px), linear-gradient(90deg, #333 1px, transparent 1px)',
                backgroundSize: '20px 20px'
              }}
            >
              <div style={getPreviewStyle()}>
                {formData.uppercase
                  ? 'ESTE É UM TEXTO DE EXEMPLO PARA A LEGENDA'
                  : 'Este é um texto de exemplo para a legenda'}
                <br />
                {formData.max_lines && formData.max_lines > 1
                  ? formData.uppercase
                    ? 'SEGUNDA LINHA DE DEMONSTRAÇÃO'
                    : 'Segunda linha de demonstração'
                  : ''}
              </div>
            </div>
          </div>
        </div>

        {/* List Presets */}
        <div className="cyber-panel p-6 overflow-y-auto">
          <h2 className="text-xl font-bold text-white mb-4">Presets Salvos</h2>

          <div className="space-y-3">
            {presets.length === 0 ? (
              <p className="text-gray-500 italic">Nenhum preset cadastrado.</p>
            ) : (
              presets.map((preset) => (
                <div
                  key={preset.id}
                  className="bg-cyber-bg border border-cyber-border p-4 rounded-lg flex items-center justify-between hover:border-neon-blue transition-colors"
                >
                  <div>
                    <h3 className="font-bold text-white text-lg">{preset.name}</h3>
                    <div className="text-sm text-gray-400 mt-1 space-x-3">
                      <span>Fonte: {preset.font}</span>
                      <span>Tam: {preset.size}px</span>
                      <span>Alinhamento: {preset.alignment}</span>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => startEdit(preset)}
                      className="p-2 text-gray-400 hover:text-neon-blue transition-colors rounded"
                      title="Editar"
                    >
                      <Edit className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleDelete(preset.id)}
                      className="p-2 text-gray-400 hover:text-neon-pink transition-colors rounded"
                      title="Excluir"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
