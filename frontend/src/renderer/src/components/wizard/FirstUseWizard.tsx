import { useState, useEffect } from 'react'
import { CheckCircle2, ChevronRight, Settings as SettingsIcon, Monitor, HardDrive } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { api } from '../../services/api'
import { useToast } from '../../contexts/ToastContext'

interface FirstUseWizardProps {
  onComplete: () => void
}

export function FirstUseWizard({ onComplete }: FirstUseWizardProps) {
  const [step, setStep] = useState(1)
  const [workspace, setWorkspace] = useState('')
  const [loading, setLoading] = useState(false)
  const [hardware, setHardware] = useState<any>(null)
  const { showToast } = useToast()

  useEffect(() => {
    // Basic hardware fetch just to show something cool
    api.get<any>('/hardware/snapshot').then(res => setHardware(res?.data || res)).catch(() => {})
  }, [])

  const finishWizard = async () => {
    setLoading(true)
    try {
      if (workspace) {
        await api.put<any>('/settings/key/default_project_path', { value: workspace })
      }
      await api.put<any>('/settings/key/first_run_completed', { value: "true" })
      showToast('Configuração concluída!', 'success')
      onComplete()
    } catch (error) {
      showToast('Erro ao salvar configurações.', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <Card className="w-full max-w-2xl bg-zinc-900 border-zinc-800 shadow-2xl">
        <CardHeader>
          <CardTitle className="text-2xl flex items-center gap-2 text-primary-400">
            <SettingsIcon className="h-6 w-6" />
            Bem-vindo ao AUTOMA
          </CardTitle>
          <div className="text-sm text-gray-400 mt-2">
            Vamos preparar seu ambiente para processamento em lote.
          </div>
        </CardHeader>
        
        <CardContent className="min-h-[250px]">
          {step === 1 && (
            <div className="space-y-4 animate-in fade-in">
              <h3 className="text-lg font-medium text-white flex items-center gap-2">
                <HardDrive className="h-5 w-5" />
                Espaço de Trabalho (Workspace)
              </h3>
              <p className="text-zinc-400 text-sm">
                Onde o AUTOMA deve salvar os projetos e arquivos gerados por padrão?
              </p>
              <div className="flex gap-2 mt-4">
                <Input
                  placeholder="Ex: C:\Users\Projetos\Automa"
                  value={workspace}
                  onChange={(e) => setWorkspace(e.target.value)}
                  className="flex-1"
                />
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4 animate-in fade-in">
              <h3 className="text-lg font-medium text-white flex items-center gap-2">
                <Monitor className="h-5 w-5" />
                Hardware Detectado
              </h3>
              <p className="text-zinc-400 text-sm">
                O AUTOMA analisou seu sistema e configurou o processamento paralelo.
              </p>
              
              <div className="bg-zinc-800/50 p-4 rounded-lg space-y-3 mt-4 border border-zinc-700">
                <div className="flex justify-between items-center">
                  <span className="text-zinc-400">CPU:</span>
                  <span className="font-mono text-zinc-200">
                    {hardware ? `${hardware.cpu_percent}% Uso` : 'Detectando...'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-zinc-400">RAM:</span>
                  <span className="font-mono text-zinc-200">
                    {hardware ? `${(hardware.ram_used / 1e9).toFixed(1)}GB / ${(hardware.ram_total / 1e9).toFixed(1)}GB` : 'Detectando...'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-zinc-400">Aceleração GPU:</span>
                  <span className="font-mono text-emerald-400 font-medium">
                    {hardware?.gpus?.length ? 'Disponível' : 'Não Detectada'}
                  </span>
                </div>
              </div>
            </div>
          )}
        </CardContent>

        <div className="flex justify-between border-t border-zinc-800 pt-6 p-6">
          <div className="flex gap-2">
            <div className={`h-2 w-2 rounded-full ${step >= 1 ? 'bg-primary-500' : 'bg-zinc-700'}`} />
            <div className={`h-2 w-2 rounded-full ${step >= 2 ? 'bg-primary-500' : 'bg-zinc-700'}`} />
          </div>
          
          <div className="flex gap-3">
            {step > 1 && (
              <Button variant="secondary" onClick={() => setStep(step - 1)}>
                Voltar
              </Button>
            )}
            
            {step < 2 ? (
              <Button onClick={() => setStep(step + 1)}>
                Continuar
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            ) : (
              <Button 
                onClick={finishWizard} 
                disabled={loading}
                className="bg-emerald-600 hover:bg-emerald-700 text-white"
              >
                <CheckCircle2 className="h-4 w-4 mr-2" />
                {loading ? 'Salvando...' : 'Concluir'}
              </Button>
            )}
          </div>
        </div>
      </Card>
    </div>
  )
}
