import React, { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card'
import { Input } from '../ui/Input'
import { Button } from '../ui/Button'
import { useToast } from '../../contexts/ToastContext'
import { settingsService } from '../../services/settingsService'
import { AppSettings } from '../../types/settings'
import { Settings, Cpu, HardDrive } from 'lucide-react'

export const SettingsForm: React.FC = () => {
  const { showToast } = useToast()
  const [loading, setLoading] = useState(false)
  const [settings, setSettings] = useState<AppSettings>({
    language: 'pt-BR',
    theme: 'cyberpunk',
    default_projects_dir: '',
    max_processes: 4,
    max_cpu_usage: 80,
    max_ram_usage: 80,
    max_gpu_usage: 80,
    max_workers: 4,
    process_priority: 'Normal'
  })

  // Load settings on load
  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const response = await settingsService.list()
        const newSettings = { ...settings }
        response.settings.forEach((s) => {
          if (s.key in newSettings) {
            const val = s.type === 'number' ? Number(s.value) : s.value
            newSettings[s.key] = val
          }
        })
        setSettings(newSettings as AppSettings)
      } catch (err) {
        console.error('Failed to load settings:', err)
      }
    }
    fetchSettings()
  }, [])

  const handleChange = (key: keyof AppSettings, value: any) => {
    setSettings((prev) => ({
      ...prev,
      [key]: value
    }))
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Upsert all keys
      const promises = Object.entries(settings).map(([key, value]) => {
        const type = typeof value === 'number' ? 'number' : 'string'
        let category: 'general' | 'performance' | 'paths' = 'general'
        if (key.includes('max_') || key.includes('processes') || key.includes('priority')) {
          category = 'performance'
        } else if (key.includes('dir') || key.includes('path')) {
          category = 'paths'
        }

        return settingsService.create({
          key,
          value: String(value),
          type,
          category
        })
      })

      await Promise.all(promises)
      showToast('Configurações salvas automaticamente com sucesso!', 'success')
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Falha ao salvar configurações', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSave} className="space-y-6">
      {/* General Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-neon-cyan" />
            <span>Configurações Gerais</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex flex-col gap-1.5 w-full">
            <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">
              Idioma
            </label>
            <select
              value={settings.language}
              onChange={(e) => handleChange('language', e.target.value)}
              className="w-full bg-cyber-bg border border-cyber-border focus:border-neon-green/60 text-sm text-white rounded px-3 py-2 outline-none cursor-pointer"
            >
              <option value="pt-BR">Português (Brasil)</option>
              <option value="en-US">English (United States)</option>
            </select>
          </div>

          <div className="flex flex-col gap-1.5 w-full">
            <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">
              Tema Visual
            </label>
            <select
              value={settings.theme}
              onChange={(e) => handleChange('theme', e.target.value)}
              className="w-full bg-cyber-bg border border-cyber-border focus:border-neon-green/60 text-sm text-white rounded px-3 py-2 outline-none cursor-pointer"
            >
              <option value="cyberpunk">Cyberpunk Neon</option>
              <option value="dark">Cinza Escuro Profissional</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Directory Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <HardDrive className="w-5 h-5 text-neon-cyan" />
            <span>Diretórios e Caminhos</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Input
            label="Pasta Padrão de Projetos"
            placeholder="Ex: C:\Users\nome\AUTOMA\projects"
            value={settings.default_projects_dir}
            onChange={(e) => handleChange('default_projects_dir', e.target.value)}
            disabled={loading}
          />
        </CardContent>
      </Card>

      {/* Performance Throttling */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-neon-pink" />
            <span>Controles de Performance e Limites</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Input
            label="Processos Simultâneos Máximos"
            type="number"
            min={1}
            max={16}
            value={settings.max_processes}
            onChange={(e) => handleChange('max_processes', Number(e.target.value))}
            disabled={loading}
          />

          <Input
            label="Uso Limite da CPU (%)"
            type="number"
            min={10}
            max={100}
            value={settings.max_cpu_usage}
            onChange={(e) => handleChange('max_cpu_usage', Number(e.target.value))}
            disabled={loading}
          />

          <Input
            label="Uso Limite da Memória RAM (%)"
            type="number"
            min={10}
            max={100}
            value={settings.max_ram_usage}
            onChange={(e) => handleChange('max_ram_usage', Number(e.target.value))}
            disabled={loading}
          />

          <Input
            label="Uso Limite da GPU (%)"
            type="number"
            min={10}
            max={100}
            value={settings.max_gpu_usage}
            onChange={(e) => handleChange('max_gpu_usage', Number(e.target.value))}
            disabled={loading}
          />
          <Input
            label="Limite Máximo de Workers"
            type="number"
            min={1}
            max={16}
            value={settings.max_workers}
            onChange={(e) => handleChange('max_workers', Number(e.target.value))}
            disabled={loading}
          />

          <div className="flex flex-col gap-1.5 w-full">
            <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">
              Prioridade do Processo
            </label>
            <select
              value={settings.process_priority}
              onChange={(e) => handleChange('process_priority', e.target.value)}
              className="w-full bg-cyber-bg border border-cyber-border focus:border-neon-green/60 text-sm text-white rounded px-3 py-2 outline-none cursor-pointer"
              disabled={loading}
            >
              <option value="Baixa">Baixa (Segundo Plano)</option>
              <option value="Normal">Normal (Padrão)</option>
              <option value="Alta">Alta (Máximo Desempenho)</option>
            </select>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end pt-3">
        <Button type="submit" variant="primary" isLoading={loading}>
          Salvar Configurações
        </Button>
      </div>
    </form>
  )
}
