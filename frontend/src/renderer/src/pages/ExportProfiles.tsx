import React, { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { useToast } from '../contexts/ToastContext'
import { exportProfileService } from '../services/exportProfileService'
import { ExportProfile } from '../types/exportProfile'
import { Plus, Edit3, Trash2, X, Settings, Download } from 'lucide-react'

export const ExportProfiles: React.FC = () => {
  const { showToast } = useToast()

  const [profiles, setProfiles] = useState<ExportProfile[]>([])
  const [loading, setLoading] = useState(false)

  const [isEditing, setIsEditing] = useState(false)
  const [editingProfile, setEditingProfile] = useState<ExportProfile | null>(null)

  // Form State
  const [formName, setFormName] = useState('')
  const [formDesc, setFormDesc] = useState('')
  const [formFormat, setFormFormat] = useState<'mp4' | 'mov' | 'mkv'>('mp4')
  const [formResolution, setFormResolution] = useState('1080x1920')
  const [formFps, setFormFps] = useState(30)
  const [formVideoCodec, setFormVideoCodec] = useState('h264')
  const [formAudioCodec, setFormAudioCodec] = useState('aac')
  const [formVideoBitrate, setFormVideoBitrate] = useState('5M')
  const [formAudioBitrate, setFormAudioBitrate] = useState('192k')
  const [formPreset, setFormPreset] = useState('medium')

  const fetchProfiles = async () => {
    setLoading(true)
    try {
      const data = await exportProfileService.getAll()
      setProfiles(data)
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Falha ao buscar perfis', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProfiles()
  }, [])

  const startNew = () => {
    setEditingProfile(null)
    setFormName('')
    setFormDesc('')
    setFormFormat('mp4')
    setFormResolution('1080x1920')
    setFormFps(30)
    setFormVideoCodec('h264')
    setFormAudioCodec('aac')
    setFormVideoBitrate('5M')
    setFormAudioBitrate('192k')
    setFormPreset('medium')
    setIsEditing(true)
  }

  const startEdit = (p: ExportProfile) => {
    setEditingProfile(p)
    setFormName(p.name)
    setFormDesc(p.description)
    setFormFormat(p.format)
    setFormResolution(p.resolution)
    setFormFps(p.fps)
    setFormVideoCodec(p.video_codec)
    setFormAudioCodec(p.audio_codec)
    setFormVideoBitrate(p.video_bitrate)
    setFormAudioBitrate(p.audio_bitrate)
    setFormPreset(p.preset)
    setIsEditing(true)
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Deseja realmente excluir este perfil de exportação?')) return
    try {
      await exportProfileService.delete(id)
      showToast('Perfil excluído com sucesso!', 'success')
      fetchProfiles()
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Falha ao deletar', 'error')
    }
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formName.trim()) {
      showToast('O nome do perfil é obrigatório', 'error')
      return
    }

    const payload = {
      name: formName,
      description: formDesc,
      format: formFormat,
      resolution: formResolution,
      fps: formFps,
      video_codec: formVideoCodec,
      audio_codec: formAudioCodec,
      video_bitrate: formVideoBitrate,
      audio_bitrate: formAudioBitrate,
      preset: formPreset
    }

    try {
      if (editingProfile) {
        await exportProfileService.update(editingProfile.id, payload)
        showToast('Perfil atualizado!', 'success')
      } else {
        await exportProfileService.create(payload)
        showToast('Perfil criado!', 'success')
      }
      setIsEditing(false)
      fetchProfiles()
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Falha ao salvar', 'error')
    }
  }

  if (isEditing) {
    return (
      <div className="space-y-6 h-full flex flex-col min-h-0 select-none">
        <form onSubmit={handleSave} className="max-w-2xl mx-auto w-full space-y-6">
          <Card>
            <CardHeader className="flex flex-row justify-between items-center pb-2">
              <CardTitle className="text-sm font-semibold tracking-wider text-neon-pink flex items-center gap-2 uppercase">
                <Settings className="w-4 h-4" />
                <span>Perfil de Exportação</span>
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
                  Nome
                </label>
                <input
                  type="text"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  className="bg-cyber-bg border border-cyber-border focus:border-neon-pink/60 text-sm text-white rounded p-2 outline-none font-sans"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">
                    Resolução
                  </label>
                  <select
                    value={formResolution}
                    onChange={(e) => setFormResolution(e.target.value)}
                    className="bg-cyber-bg border border-cyber-border text-sm text-white rounded p-2 outline-none"
                  >
                    <option value="1080x1920">Vertical (1080x1920)</option>
                    <option value="1920x1080">Horizontal (1920x1080)</option>
                    <option value="1080x1080">Quadrado (1080x1080)</option>
                    <option value="720x1280">Vertical HD (720x1280)</option>
                  </select>
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">
                    Formato
                  </label>
                  <select
                    value={formFormat}
                    onChange={(e) => setFormFormat(e.target.value as any)}
                    className="bg-cyber-bg border border-cyber-border text-sm text-white rounded p-2 outline-none"
                  >
                    <option value="mp4">MP4</option>
                    <option value="mov">MOV</option>
                    <option value="mkv">MKV</option>
                  </select>
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">
                    FPS
                  </label>
                  <select
                    value={formFps}
                    onChange={(e) => setFormFps(Number(e.target.value))}
                    className="bg-cyber-bg border border-cyber-border text-sm text-white rounded p-2 outline-none"
                  >
                    <option value={30}>30 FPS</option>
                    <option value={60}>60 FPS</option>
                    <option value={24}>24 FPS</option>
                  </select>
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">
                    Codec de Vídeo
                  </label>
                  <select
                    value={formVideoCodec}
                    onChange={(e) => setFormVideoCodec(e.target.value)}
                    className="bg-cyber-bg border border-cyber-border text-sm text-white rounded p-2 outline-none"
                  >
                    <option value="h264">H.264</option>
                    <option value="hevc">H.265 (HEVC)</option>
                    <option value="libx264">libx264 (Software)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">
                    Bitrate de Vídeo
                  </label>
                  <input
                    type="text"
                    value={formVideoBitrate}
                    onChange={(e) => setFormVideoBitrate(e.target.value)}
                    className="bg-cyber-bg border border-cyber-border text-sm text-white rounded p-2 outline-none"
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">
                    Preset FFmpeg
                  </label>
                  <select
                    value={formPreset}
                    onChange={(e) => setFormPreset(e.target.value)}
                    className="bg-cyber-bg border border-cyber-border text-sm text-white rounded p-2 outline-none"
                  >
                    <option value="ultrafast">Ultrafast</option>
                    <option value="fast">Fast</option>
                    <option value="medium">Medium</option>
                    <option value="slow">Slow</option>
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end gap-3 pt-3">
            <Button type="button" variant="secondary" onClick={() => setIsEditing(false)}>
              Cancelar
            </Button>
            <Button type="submit" variant="primary">
              Salvar Perfil
            </Button>
          </div>
        </form>
      </div>
    )
  }

  return (
    <div className="space-y-6 h-full flex flex-col min-h-0 select-none">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 shrink-0">
        <div>
          <h2 className="text-xl font-bold tracking-wider text-white">Perfis de Exportação</h2>
          <p className="text-xs font-mono text-gray-500 mt-1 uppercase">
            Formatos e codecs para renderização
          </p>
        </div>
        <Button
          variant="primary"
          className="flex items-center gap-2 text-xs font-mono bg-neon-pink text-black hover:bg-neon-pink/80"
          onClick={startNew}
        >
          <Plus className="w-4 h-4" />
          <span>Criar Perfil</span>
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="text-gray-400 text-sm font-mono p-4">Carregando...</div>
        ) : profiles.length === 0 ? (
          <div className="text-gray-500 text-sm font-mono p-4">
            Nenhum perfil de exportação encontrado.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {profiles.map((profile) => (
              <Card key={profile.id} className="hover:border-neon-pink/40 transition-colors">
                <CardContent className="p-4 flex flex-col justify-between h-full space-y-4">
                  <div>
                    <h3 className="text-white font-bold text-sm mb-1 truncate flex items-center gap-2">
                      <Download className="w-4 h-4 text-neon-pink" />
                      {profile.name}
                    </h3>
                    <p className="text-xs text-gray-500 font-mono mt-2">
                      {profile.resolution} • {profile.fps}fps • {(profile.format ?? 'mp4').toUpperCase()}
                    </p>
                    <p className="text-xs text-gray-500 font-mono">
                      {profile.video_codec} • {profile.video_bitrate}
                    </p>
                  </div>
                  <div className="flex gap-2 justify-end mt-auto">
                    <Button variant="secondary" size="sm" onClick={() => startEdit(profile)}>
                      <Edit3 className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleDelete(profile.id)}
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
