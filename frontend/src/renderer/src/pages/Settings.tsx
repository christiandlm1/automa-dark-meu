import React from 'react'
import { SettingsForm } from '../components/settings/SettingsForm'
import { Button } from '../components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { HardDrive, Download, Trash } from 'lucide-react'
import { api } from '../services/api'
import { useToast } from '../contexts/ToastContext'

export const Settings: React.FC = () => {
  const { showToast } = useToast()
  return (
    <div className="max-w-4xl mx-auto space-y-6 select-none">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold tracking-wider text-white">Configurações do Software</h2>
        <p className="text-xs font-mono text-gray-500 mt-1 uppercase">
          Ajuste as preferências gerais, diretórios e limites de processamento
        </p>
      </div>

      {/* Settings Form */}
      <SettingsForm />

      {/* Manutenção */}
      <Card className="bg-cyber-panel/50 border-cyber-border/50">
        <CardHeader>
          <CardTitle className="text-lg font-mono text-white flex items-center gap-2">
            <HardDrive className="h-5 w-5 text-neon-cyan" />
            Manutenção do Sistema
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <Button 
              variant="secondary" 
              className="flex-1"
              onClick={async () => {
                try {
                  const res = await api.post<any>('/settings/maintenance/backup_db')
                  showToast('Backup Criado: ' + (res.backup_path || res.data?.backup_path), 'success')
                } catch {
                  showToast('Falha ao criar backup', 'error')
                }
              }}
            >
              <Download className="h-4 w-4 mr-2" />
              Backup do Banco de Dados
            </Button>
            <Button 
              variant="secondary" 
              className="flex-1"
              onClick={async () => {
                try {
                  await api.post('/settings/maintenance/clear_cache')
                  showToast('Cache limpo com sucesso', 'success')
                } catch {
                  showToast('Falha ao limpar cache', 'error')
                }
              }}
            >
              <Trash className="h-4 w-4 mr-2" />
              Limpar Cache
            </Button>
            <Button 
              variant="secondary" 
              className="flex-1"
              onClick={() => {
                window.open(`/api/settings/maintenance/diagnostics`, '_blank')
              }}
            >
              <HardDrive className="h-4 w-4 mr-2" />
              Exportar Diagnósticos
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
