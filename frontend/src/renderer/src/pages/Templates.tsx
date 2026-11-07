import React, { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { useProject } from '../contexts/ProjectContext'
import { useToast } from '../contexts/ToastContext'
import { videoTemplateService } from '../services/videoTemplateService'
import { subtitlePresetService } from '../services/subtitlePresetService'
import { assetService, Asset } from '../services/assetService'
import { VideoTemplate, PipelineNode } from '../types/videoTemplate'
import { SubtitlePreset } from '../types/subtitlePreset'
import { Plus, Edit3, Trash2, X, Settings, Download, Upload } from 'lucide-react'
import { api } from '../services/api'

export const Templates: React.FC = () => {
  const { activeProject } = useProject()
  const { showToast } = useToast()

  const [templates, setTemplates] = useState<VideoTemplate[]>([])
  const [subtitlePresets, setSubtitlePresets] = useState<SubtitlePreset[]>([])
  const [backgroundAssets, setBackgroundAssets] = useState<Asset[]>([])
  const [loading, setLoading] = useState(false)

  const [isEditing, setIsEditing] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState<VideoTemplate | null>(null)

  // Flat fields
  const [formName, setFormName] = useState('')
  const [formBackground, setFormBackground] = useState('')
  const [formSmartFit, setFormSmartFit] = useState(true)
  const [formSubtitlePreset, setFormSubtitlePreset] = useState<string>('')
  const [formZoom, setFormZoom] = useState(1.0)
  const [formCrop, setFormCrop] = useState('9:16')
  const [formMetadataRemove, setFormMetadataRemove] = useState(true)

  const fetchTemplates = async () => {
    setLoading(true)
    try {
      const response = await videoTemplateService.list()
      setTemplates(response.templates)

      const presets = await subtitlePresetService.list()
      setSubtitlePresets(presets)

      const images = await assetService.getAssets('image_background')
      const videos = await assetService.getAssets('video_background')
      setBackgroundAssets([...images, ...videos])
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Falha ao buscar dados', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTemplates()
  }, [activeProject])

  const startNew = () => {
    setEditingTemplate(null)
    setFormName('')
    setFormBackground('')
    setFormSmartFit(true)
    setFormSubtitlePreset('')
    setFormZoom(1.0)
    setFormCrop('9:16')
    setFormMetadataRemove(true)
    setIsEditing(true)
  }

  const startEdit = (template: VideoTemplate) => {
    setEditingTemplate(template)
    setFormName(template.name)

    // Parse from pipeline_config
    let parsedBg = ''
    let parsedSmartFit = false
    let parsedSub = ''
    let parsedZoom = 1.0
    let parsedCrop = '9:16'
    let parsedMeta = false

    template.pipeline_config?.forEach((node) => {
      if (node.type === 'crop') {
        parsedCrop = node.config.aspect_ratio || '9:16'
      } else if (node.type === 'zoom') {
        parsedZoom = node.config.factor || 1.0
      } else if (node.type === 'metadatacleaner') {
        parsedMeta = true
      } else if (node.type === 'background') {
        parsedBg = node.config.asset_id || ''
        parsedSmartFit = !!node.config.smart_fit
      } else if (node.type === 'subtitle') {
        parsedSub = node.config.preset_id || ''
      }
    })

    setFormBackground(parsedBg)
    setFormSmartFit(parsedSmartFit)
    setFormSubtitlePreset(parsedSub)
    setFormZoom(parsedZoom)
    setFormCrop(parsedCrop)
    setFormMetadataRemove(parsedMeta)

    setIsEditing(true)
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Deseja realmente excluir este template?')) return
    try {
      await videoTemplateService.delete(id)
      showToast('Template excluído com sucesso!', 'success')
      fetchTemplates()
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Falha ao deletar', 'error')
    }
  }

  const handleExport = (id: string) => {
    window.open(`http://localhost:8420/api/video-templates/${id}/export`, '_blank')
  }

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    try {
      // Do not set Content-Type here: the browser must add the multipart boundary itself,
      // otherwise the backend cannot parse the upload and answers 400.
      await api.post('/video-templates/import', formData)
      showToast('Template importado com sucesso!', 'success')
      fetchTemplates()
    } catch (err) {
      const reason = err instanceof Error && err.message ? `: ${err.message}` : ''
      showToast(`Falha ao importar template${reason}`, 'error')
    } finally {
      // Allow selecting the same file again after a failure.
      e.target.value = ''
    }
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formName.trim()) {
      showToast('O nome do template é obrigatório', 'error')
      return
    }

    const pipeline_config: PipelineNode[] = [
      { type: 'import', config: {} },
      { type: 'crop', config: { aspect_ratio: formCrop } },
      { type: 'zoom', config: { factor: formZoom } }
    ]

    if (formBackground) {
      pipeline_config.push({
        type: 'background',
        config: { asset_id: formBackground, ...(formSmartFit ? { smart_fit: true } : {}) }
      })
    }

    if (formSubtitlePreset) {
      pipeline_config.push({ type: 'subtitle', config: { preset_id: formSubtitlePreset } })
    }

    if (formMetadataRemove) {
      pipeline_config.push({ type: 'metadatacleaner', config: {} })
    }

    try {
      if (editingTemplate) {
        await videoTemplateService.update(editingTemplate.id, {
          name: formName,
          pipeline_config
        })
        showToast('Template atualizado!', 'success')
      } else {
        await videoTemplateService.create({
          name: formName,
          pipeline_config
        })
        showToast('Template criado!', 'success')
      }
      setIsEditing(false)
      fetchTemplates()
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Falha ao salvar', 'error')
    }
  }

  if (isEditing) {
    return (
      <div className="space-y-6 h-full flex flex-col min-h-0 select-none">
        <div className="flex-1 flex flex-col lg:flex-row gap-6 min-h-0 overflow-hidden">
          <form
            onSubmit={handleSave}
            className="flex-1 overflow-y-auto pr-2 space-y-6 max-w-2xl mx-auto w-full"
          >
            <Card>
              <CardHeader className="flex flex-row justify-between items-center pb-2">
                <CardTitle className="text-sm font-semibold tracking-wider text-neon-green flex items-center gap-2 uppercase">
                  <Settings className="w-4 h-4" />
                  <span>Configurações do Template</span>
                </CardTitle>
                <button
                  type="button"
                  onClick={() => setIsEditing(false)}
                  className="text-gray-500 hover:text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">
                    Nome do Template
                  </label>
                  <input
                    type="text"
                    value={formName}
                    onChange={(e) => setFormName(e.target.value)}
                    placeholder="Ex: Template Shorts"
                    className="bg-cyber-bg border border-cyber-border focus:border-neon-green/60 text-sm text-white rounded p-2 outline-none font-sans"
                  />
                </div>

                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">
                    Fundo (Background)
                  </label>
                  <select
                    value={formBackground}
                    onChange={(e) => setFormBackground(e.target.value)}
                    className="bg-cyber-bg border border-cyber-border text-sm text-white rounded p-2 outline-none font-sans"
                  >
                    <option value="">Automático (Desfoque ou Nenhum)</option>
                    {backgroundAssets.map((asset) => (
                      <option key={asset.id} value={asset.id}>
                        {asset.name} ({asset.category || 'Default'})
                      </option>
                    ))}
                  </select>
                  {formBackground && (
                    <label className="flex items-start gap-2 mt-2 text-xs text-gray-300 font-sans cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formSmartFit}
                        onChange={(e) => setFormSmartFit(e.target.checked)}
                        className="mt-0.5"
                      />
                      <span>
                        <b className="text-neon-green">Ajuste inteligente do vídeo:</b> remove bordas
                        pretas/brancas e templates antigos do vídeo e o encaixa, sem distorcer, na área
                        livre abaixo do texto deste fundo.
                      </span>
                    </label>
                  )}
                </div>

                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">
                    Estilo de Legenda
                  </label>
                  <select
                    value={formSubtitlePreset}
                    onChange={(e) => setFormSubtitlePreset(e.target.value)}
                    className="bg-cyber-bg border border-cyber-border text-sm text-white rounded p-2 outline-none font-sans"
                  >
                    <option value="">Nenhuma</option>
                    {subtitlePresets.map((preset) => (
                      <option key={preset.id} value={preset.id}>
                        {preset.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono flex justify-between">
                    <span>Zoom ({formZoom.toFixed(1)}x)</span>
                  </label>
                  <input
                    type="range"
                    min={1.0}
                    max={3.0}
                    step={0.1}
                    value={formZoom}
                    onChange={(e) => setFormZoom(Number(e.target.value))}
                    className="accent-neon-green"
                  />
                </div>

                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">
                    Formato (Crop)
                  </label>
                  <select
                    value={formCrop}
                    onChange={(e) => setFormCrop(e.target.value)}
                    className="bg-cyber-bg border border-cyber-border text-sm text-white rounded p-2 outline-none font-sans"
                  >
                    <option value="9:16">9:16 (Vertical)</option>
                    <option value="1:1">1:1 (Quadrado)</option>
                    <option value="16:9">16:9 (Horizontal)</option>
                  </select>
                </div>

                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={formMetadataRemove}
                    onChange={(e) => setFormMetadataRemove(e.target.checked)}
                    id="meta-remove"
                    className="w-4 h-4 accent-neon-green cursor-pointer"
                  />
                  <label
                    htmlFor="meta-remove"
                    className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono cursor-pointer"
                  >
                    Remover Metadados (Limpeza)
                  </label>
                </div>
              </CardContent>
            </Card>

            <div className="flex justify-end gap-3 pt-3">
              <Button type="button" variant="secondary" onClick={() => setIsEditing(false)}>
                Cancelar
              </Button>
              <Button type="submit" variant="primary">
                Salvar
              </Button>
            </div>
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 h-full flex flex-col min-h-0 select-none">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 shrink-0">
        <div>
          <h2 className="text-xl font-bold tracking-wider text-white">Templates</h2>
          <p className="text-xs font-mono text-gray-500 mt-1 uppercase">
            Gerencie configurações de processamento
          </p>
        </div>
        <div className="flex gap-2">
          <input type="file" id="import-template" accept=".automa_template,.json,.zip" className="hidden" onChange={handleImport} />
          <Button
            variant="secondary"
            className="flex items-center gap-2 text-xs font-mono"
            onClick={() => document.getElementById('import-template')?.click()}
          >
            <Upload className="w-4 h-4" />
            <span>Importar</span>
          </Button>
          <Button
            variant="primary"
            className="flex items-center gap-2 text-xs font-mono"
            onClick={startNew}
          >
            <Plus className="w-4 h-4" />
            <span>Criar Template</span>
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="text-gray-400 text-sm font-mono p-4">Carregando...</div>
        ) : templates.length === 0 ? (
          <div className="text-gray-500 text-sm font-mono p-4">Nenhum template encontrado.</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {templates.map((template) => (
              <Card key={template.id} className="hover:border-neon-green/40 transition-colors">
                <CardContent className="p-4 flex flex-col justify-between h-full space-y-4">
                  <div>
                    <h3 className="text-white font-bold text-sm mb-1 truncate">{template.name}</h3>
                    <p className="text-xs text-gray-500 font-mono">
                      {template.pipeline_config?.length} nós
                    </p>
                  </div>
                  <div className="flex gap-2 justify-end mt-auto">
                    <Button variant="secondary" size="sm" onClick={() => handleExport(template.id)} title="Exportar">
                      <Download className="w-4 h-4" />
                    </Button>
                    <Button variant="secondary" size="sm" onClick={() => startEdit(template)} title="Editar">
                      <Edit3 className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleDelete(template.id)}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
