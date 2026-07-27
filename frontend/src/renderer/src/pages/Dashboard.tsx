import React, { useState, useEffect } from 'react'
import { useProject } from '../contexts/ProjectContext'
import { hardwareService } from '../services/hardwareService'
import { Hardware } from '../types/hardware'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { StatsCard } from '../components/dashboard/StatsCard'
import { Film, HardDrive, CheckCircle2, Clock, Cpu } from 'lucide-react'
import { formatBytes } from '../utils/format'

export const Dashboard: React.FC = () => {
  const { totalVideos, totalBytes, processedCount, pendingCount } = useProject()

  const [hardware, setHardware] = useState<Hardware | null>(null)
  const [loadingHw, setLoadingHw] = useState(false)

  useEffect(() => {
    const fetchHw = async () => {
      setLoadingHw(true)
      try {
        const info = await hardwareService.getInfo()
        setHardware(info)
      } catch (err) {
        console.error('Failed to fetch hardware specifications:', err)
      } finally {
        setLoadingHw(false)
      }
    }
    fetchHw()
  }, [])

  return (
    <div className="space-y-6 select-none">
      {/* Page Title */}
      <div>
        <h2 className="text-xl font-bold tracking-wider text-white">Dashboard do Projeto</h2>
        <p className="text-xs font-mono text-gray-500 mt-1 uppercase">
          Estatísticas e monitoramento em tempo real
        </p>
      </div>

      {/* Project Statistics row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Total de Vídeos"
          value={totalVideos}
          icon={Film}
          color="cyan"
          description="Vídeos catalogados"
        />
        <StatsCard
          title="Espaço Utilizado"
          value={formatBytes(totalBytes)}
          icon={HardDrive}
          color="green"
          description="Tamanho total no disco"
        />
        <StatsCard
          title="Processados"
          value={`${processedCount} / ${totalVideos}`}
          icon={CheckCircle2}
          color="pink"
          description={`${pendingCount} pendente(s)`}
        />
        <StatsCard
          title="Tempo Médio"
          value="-- : --"
          icon={Clock}
          color="green"
          description="Média por render"
        />
      </div>



      {/* Detected hardware info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-neon-cyan" />
            <span>Hardware Detectado</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loadingHw ? (
            <div className="flex justify-center items-center py-6">
              <svg className="animate-spin h-5 w-5 text-neon-green" viewBox="0 0 24 24" fill="none">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4"
                />
              </svg>
            </div>
          ) : hardware ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 text-sm font-cyber">
              {/* CPU Specs */}
              <div className="bg-cyber-surface/40 p-4 border border-cyber-border rounded-lg space-y-2">
                <span className="text-[10px] font-mono font-bold text-gray-500 uppercase block">
                  Processador (CPU)
                </span>
                <span className="text-white font-bold block truncate" title={hardware.cpu_name}>
                  {hardware.cpu_name}
                </span>
                <span className="text-xs text-gray-400 font-mono block">
                  Cores: {hardware.cpu_cores} | Threads: {hardware.cpu_threads}
                </span>
              </div>

              {/* RAM Specs */}
              <div className="bg-cyber-surface/40 p-4 border border-cyber-border rounded-lg space-y-2">
                <span className="text-[10px] font-mono font-bold text-gray-500 uppercase block">
                  Memória RAM Inst.
                </span>
                <span className="text-white font-bold block">
                  {hardware.ram_total_gb.toFixed(1)} GB
                </span>
                <span className="text-xs text-gray-400 font-mono block">
                  DDR / Capacidade Física
                </span>
              </div>

              {/* GPU Specs */}
              <div className="bg-cyber-surface/40 p-4 border border-cyber-border rounded-lg space-y-2">
                <span className="text-[10px] font-mono font-bold text-gray-500 uppercase block">
                  Placa de Vídeo (GPU)
                </span>
                <span
                  className="text-white font-bold block truncate"
                  title={hardware.gpu_name || 'Integrada / Padrão'}
                >
                  {hardware.gpu_name || 'Não Identificada'}
                </span>
                <span className="text-xs text-gray-400 font-mono block">
                  Memória Dedicada:{' '}
                  {hardware.gpu_memory_gb ? `${hardware.gpu_memory_gb.toFixed(1)} GB` : '-'}
                </span>
              </div>

              {/* System Specs */}
              <div className="bg-cyber-surface/40 p-4 border border-cyber-border rounded-lg space-y-2 sm:col-span-2 md:col-span-3">
                <span className="text-[10px] font-mono font-bold text-gray-500 uppercase block">
                  Sistema Operacional
                </span>
                <div className="flex items-center gap-3 text-white font-bold">
                  <span>{hardware.os_name}</span>
                  <span className="text-xs text-gray-400 font-mono font-normal">
                    Versão: {hardware.os_version}
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-6 text-xs font-mono text-gray-500">
              Nenhuma informação de hardware disponível
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
