import React from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card'
import { useWebSocket } from '../../hooks/useWebSocket'
import { HardwareMonitorResponse } from '../../types/hardware'
import { Cpu, Database, Activity } from 'lucide-react'
import { ProgressBar } from '../ui/ProgressBar'

export const HardwareMonitor: React.FC = () => {
  const { data: telemetry, connected } = useWebSocket<HardwareMonitorResponse>('/hardware')

  return (
    <Card className="col-span-1 md:col-span-2">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-neon-green" />
          <span>Monitoramento de Hardware (Tempo Real)</span>
        </CardTitle>
        <div className="flex items-center gap-1.5 text-[10px] font-mono">
          <span
            className={`w-2 h-2 rounded-full ${connected ? 'bg-neon-green animate-pulse' : 'bg-neon-pink'}`}
          />
          <span className={connected ? 'text-neon-green' : 'text-neon-pink'}>
            {connected ? 'TELEMETRIA ATIVA' : 'TELEMETRIA DESCONECTADA'}
          </span>
        </div>
      </CardHeader>

      <CardContent>
        {telemetry ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* CPU Monitor */}
            <div className="space-y-4 border-b md:border-b-0 md:border-r border-cyber-border pb-6 md:pb-0 md:pr-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-neon-green" />
                  <span className="text-sm font-semibold text-white">CPU</span>
                </div>
                <span className="text-xs font-mono text-gray-400">Total</span>
              </div>
              <ProgressBar value={telemetry.cpu_percent} color="green" showText />

              {/* Cores Subgrid */}
              <div className="space-y-1.5 pt-2">
                <span className="text-[9px] uppercase font-mono font-bold text-gray-500 block">
                  Uso por Núcleo
                </span>
                <div className="grid grid-cols-4 gap-2">
                  {telemetry.cpu_per_core?.map((corePercent, idx) => (
                    <div
                      key={idx}
                      className="bg-cyber-bg border border-cyber-border/40 p-1 text-center rounded"
                    >
                      <span className="text-[8px] font-mono text-gray-500 block">C{idx}</span>
                      <span className="text-[10px] font-mono font-bold text-white block">
                        {Math.round(corePercent)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* RAM Monitor */}
            <div className="space-y-4 border-b md:border-b-0 md:border-r border-cyber-border pb-6 md:pb-0 md:pr-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4 text-neon-cyan" />
                  <span className="text-sm font-semibold text-white">Memória RAM</span>
                </div>
                <span className="text-xs font-mono text-gray-400">
                  {telemetry.ram.available_gb} GB Disp.
                </span>
              </div>
              <ProgressBar value={telemetry.ram.used_percent} color="cyan" showText />

              <div className="flex justify-between text-[10px] font-mono text-gray-500 pt-2">
                <span>Total: {telemetry.ram.total_gb} GB</span>
                <span>
                  Uso: {Math.round((telemetry.ram.total_gb * telemetry.ram.used_percent) / 100)} GB
                </span>
              </div>
            </div>

            {/* GPU / Disk Monitor */}
            <div className="space-y-4">
              {telemetry.gpu ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Cpu className="w-4 h-4 text-neon-pink" />
                      <span className="text-sm font-semibold text-white">
                        GPU ({telemetry.gpu.name})
                      </span>
                    </div>
                    <span className="text-xs font-mono text-gray-400">
                      {telemetry.gpu.vram_used_gb.toFixed(1)}/
                      {telemetry.gpu.vram_total_gb.toFixed(1)} GB VRAM
                    </span>
                  </div>
                  <ProgressBar value={telemetry.gpu.load_percent} color="pink" showText />
                  <div className="flex justify-between text-[9px] font-mono text-gray-500">
                    <span>
                      Temp: {telemetry.gpu.temperature_c ? `${telemetry.gpu.temperature_c}°C` : '-'}
                    </span>
                    <span>VRAM: {Math.round(telemetry.gpu.vram_used_percent)}%</span>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Database className="w-4 h-4 text-neon-pink" />
                      <span className="text-sm font-semibold text-white">Espaço em Disco</span>
                    </div>
                    <span className="text-xs font-mono text-gray-400">
                      {telemetry.disk.free_gb} GB Livre
                    </span>
                  </div>
                  <ProgressBar value={telemetry.disk.used_percent} color="pink" showText />
                  <div className="flex justify-between text-[10px] font-mono text-gray-500">
                    <span>Total: {telemetry.disk.total_gb} GB</span>
                    <span>
                      Uso:{' '}
                      {Math.round((telemetry.disk.total_gb * telemetry.disk.used_percent) / 100)} GB
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-12 text-gray-500 font-mono text-xs select-none">
            <svg
              className="animate-spin h-5 w-5 text-neon-green mb-3"
              viewBox="0 0 24 24"
              fill="none"
            >
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
            <span>Carregando dados de telemetria...</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
