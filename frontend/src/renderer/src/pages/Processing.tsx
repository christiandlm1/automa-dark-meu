import React, { useState, useEffect, useMemo } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { TableCell } from '../components/ui/Table'
import { Button } from '../components/ui/Button'
import { ProgressBar } from '../components/ui/ProgressBar'
import { useProject } from '../contexts/ProjectContext'
import { useToast } from '../contexts/ToastContext'
import { useWebSocket } from '../hooks/useWebSocket'
import { jobService } from '../services/jobService'
import { historyService } from '../services/historyService'
import { videoTemplateService } from '../services/videoTemplateService'
import { videoService } from '../services/videoService'
import { exportProfileService } from '../services/exportProfileService'
import { Job, JobStats } from '../types/job'
import { HistoryRecord } from '../types/history'
import { VideoTemplate } from '../types/videoTemplate'
import { ExportProfile } from '../types/exportProfile'
import { Video } from '../types/video'
import { api } from '../services/api'
import {
  Play,
  XCircle,
  RefreshCw,
  Clock,
  History,
  Terminal,
  Cpu,
  HardDrive,
  PlayCircle,
  Plus,
  Sliders,
  BarChart3,
  CheckCircle,
  AlertTriangle,
  Database,
  CheckSquare,
  Gauge
} from 'lucide-react'
import { formatDuration, formatDate } from '../utils/format'
import { TableVirtuoso } from 'react-virtuoso'

interface WSProcessingPayload {
  active_workers: number
  max_workers: number
  queue_size: number
  priority: string
  running_jobs: Array<{
    id: string
    video_name: string
    progress: number
    status: string
    speed: number
    estimated_time: number
  }>
}

interface BenchmarkData {
  total_jobs: number
  avg_render_time: number
  avg_speed: number
  success_rate: number
  error_rate: number
  avg_cpu_usage: number
  avg_ram_usage: number
  avg_gpu_usage: number
  node_averages: Record<string, number>
}

export const Processing: React.FC = () => {
  const { activeProject } = useProject()
  const { showToast } = useToast()

  // Tab State: 'queue' | 'history' | 'benchmark'
  const [activeTab, setActiveTab] = useState<'queue' | 'history' | 'benchmark'>('queue')

  // Interactive Recovery State
  const [showRecoveryPrompt, setShowRecoveryPrompt] = useState(false)
  const [interruptedJobs, setInterruptedJobs] = useState<Job[]>([])

  // REST States

  const [jobs, setJobs] = useState<Job[]>([])
  const [history, setHistory] = useState<HistoryRecord[]>([])
  const [stats, setStats] = useState<JobStats | null>(null)
  const [benchmarks, setBenchmarks] = useState<BenchmarkData | null>(null)

  const [isEnqueueOpen, setIsEnqueueOpen] = useState(false)
  const [enqueueVideoIds, setEnqueueVideoIds] = useState<string[]>([])
  const [enqueueTemplateId, setEnqueueTemplateId] = useState('')
  const [enqueueExportProfileId, setEnqueueExportProfileId] = useState('')
  const [projectVideos, setProjectVideos] = useState<Video[]>([])
  const [templates, setTemplates] = useState<VideoTemplate[]>([])
  const [exportProfiles, setExportProfiles] = useState<ExportProfile[]>([])

  // Log Details Modal
  const [selectedHistory, setSelectedHistory] = useState<HistoryRecord | null>(null)

  // Real-time WebSocket connection
  const { data: wsData, connected: wsConnected } = useWebSocket<WSProcessingPayload>('/processing')

  // Hardware snapshot WebSocket connection for gauges
  const { data: hwData } = useWebSocket<any>('/hardware')

  // Load static DB logs/history
  const fetchHistory = async () => {
    if (!activeProject) return
    try {
      const response = await historyService.listByProject(activeProject.id)
      setHistory(response.history)
    } catch (err) {
      console.error(err)
    }
  }

  // Fetch benchmark calculations from REST endpoint
  const fetchBenchmarks = async () => {
    if (!activeProject) return
    try {
      const data = await api.get<BenchmarkData>(`/history/project/${activeProject.id}/benchmarks`)
      setBenchmarks(data)
    } catch (err) {
      console.error(err)
    }
  }

  // Load rest jobs list
  const fetchJobs = async () => {
    if (!activeProject) return
    try {
      const response = await jobService.listByProject(activeProject.id)
      setJobs(response.jobs)

      // Check for recovery jobs
      const stagnated = response.jobs.filter((j) => j.status === 'paused' && j.speed === 0)
      if (stagnated.length > 0 && !showRecoveryPrompt) {
        setInterruptedJobs(stagnated)
        setShowRecoveryPrompt(true)
      }

      const statsRes = await jobService.getStats(activeProject.id)
      setStats(statsRes)
    } catch (err) {
      console.error(err)
    }
  }

  const fetchEnqueueOptions = async () => {
    if (!activeProject) return
    try {
      const vResponse = await videoService.listByProject(activeProject.id)
      setProjectVideos(vResponse.videos)

      const tResponse = await videoTemplateService.list()
      setTemplates(tResponse.templates)

      const pResponse = await exportProfileService.getAll()
      setExportProfiles(pResponse)

      if (tResponse.templates.length > 0) setEnqueueTemplateId(tResponse.templates[0].id)
      if (pResponse.length > 0) setEnqueueExportProfileId(pResponse[0].id)
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    fetchJobs()
    fetchHistory()
    fetchBenchmarks()
    fetchEnqueueOptions()
  }, [activeProject])

  // Poll fallback if WS is disconnected
  useEffect(() => {
    const timer = setInterval(() => {
      if (!wsConnected) {
        fetchJobs()
      }
      fetchBenchmarks()
    }, 4000)
    return () => clearInterval(timer)
  }, [wsConnected, activeProject])

  // Map WebSocket/Stats variables
  const activeWorkersCount =
    wsConnected && wsData ? wsData.active_workers : stats?.active_workers || 0
  const maxWorkers = wsConnected && wsData ? wsData.max_workers : stats?.max_workers || 4
  const queueSize = wsConnected && wsData ? wsData.queue_size : stats?.pending || 0
  const processPriority = wsConnected && wsData ? wsData.priority : stats?.priority || 'Normal'

  // Running jobs details from WS or REST
  const runningJobsList: Array<{
    id: string
    video_name?: string
    progress: number
    status: string
    speed: number
    estimated_time: number | null
  }> =
    wsConnected && wsData && Array.isArray(wsData.running_jobs)
      ? wsData.running_jobs
      : jobs.filter((j) => j.status === 'running')

  // Merge live WebSocket progress into the queue table (REST data is only a snapshot).
  const displayJobs = useMemo(() => {
    if (!wsConnected || !wsData || !Array.isArray(wsData.running_jobs)) return jobs
    const live = new Map(wsData.running_jobs.map((j) => [j.id, j]))
    return jobs.map((job) => {
      const l = live.get(job.id)
      return l
        ? {
            ...job,
            status: l.status as Job['status'],
            progress: l.progress,
            speed: l.speed,
            estimated_time: l.estimated_time
          }
        : job
    })
  }, [jobs, wsConnected, wsData])

  // Reload the REST list whenever a job starts or finishes (set of running jobs changes).
  const wsRunning = wsData?.running_jobs
  const runningIdsKey = Array.isArray(wsRunning)
    ? wsRunning
        .map((j) => j.id)
        .sort()
        .join(',')
    : ''
  useEffect(() => {
    if (wsConnected) fetchJobs()
  }, [runningIdsKey, wsConnected])

  // Handle Quick Enqueue
  const handleEnqueue = async (e: React.FormEvent) => {
    e.preventDefault()
    if (
      !activeProject ||
      enqueueVideoIds.length === 0 ||
      !enqueueTemplateId ||
      !enqueueExportProfileId
    )
      return

    try {
      for (const videoId of enqueueVideoIds) {
        await jobService.enqueue({
          project_id: activeProject.id,
          video_id: videoId,
          template_id: enqueueTemplateId,
          export_profile_id: enqueueExportProfileId
        })
      }
      showToast(`${enqueueVideoIds.length} vídeo(s) adicionado(s) à fila!`, 'success')
      setIsEnqueueOpen(false)
      setEnqueueVideoIds([])
      fetchJobs()
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Falha ao enfileirar', 'error')
    }
  }

  // Handle Actions
  const handlePause = async (id: string) => {
    try {
      await jobService.pause(id)
      showToast('Processamento pausado (Suspenso).', 'info')
      fetchJobs()
    } catch (err) {
      showToast('Falha ao pausar', 'error')
    }
  }

  const handleResume = async (id: string) => {
    try {
      await jobService.resume(id)
      showToast('Processamento retomado.', 'success')
      fetchJobs()
    } catch (err) {
      showToast('Falha ao retomar', 'error')
    }
  }

  const handleReprocess = async (id: string) => {
    try {
      await jobService.reprocess(id)
      showToast('Job reiniciado para reprocessing!', 'success')
      fetchJobs()
    } catch (err) {
      showToast('Falha ao reprocessar', 'error')
    }
  }

  const handleCancel = async (id: string) => {
    try {
      await jobService.cancel(id)
      showToast('Processamento cancelado e encerrado.', 'warning')
      fetchJobs()
    } catch (err) {
      showToast('Falha ao cancelar', 'error')
    }
  }

  const handleClearHistory = async () => {
    if (!activeProject || !confirm('Limpar todo o histórico de processamento do projeto?')) return
    try {
      await historyService.clear(activeProject.id)
      showToast('Histórico limpo.', 'info')
      fetchHistory()
      fetchBenchmarks()
    } catch (err) {
      showToast('Falha ao limpar histórico', 'error')
    }
  }

  const handleRecoveryAction = async (action: 'continue' | 'restart' | 'cancel') => {
    try {
      for (const job of interruptedJobs) {
        if (action === 'continue') {
          await jobService.resume(job.id)
        } else if (action === 'restart') {
          await jobService.reprocess(job.id)
        } else if (action === 'cancel') {
          await jobService.cancel(job.id)
        }
      }
      showToast(`Ação aplicada a ${interruptedJobs.length} vídeo(s).`, 'success')
      setShowRecoveryPrompt(false)
      fetchJobs()
    } catch (err) {
      showToast('Erro ao aplicar ação de recuperação.', 'error')
    }
  }

  return (
    <div className="space-y-6 h-full flex flex-col min-h-0 select-none">
      {/* Header Banner */}
      <div className="flex justify-between items-center shrink-0">
        <div>
          <h2 className="text-xl font-bold tracking-wider text-white">Painel de Processamento</h2>
          <p className="text-xs font-mono text-gray-500 mt-1 uppercase">
            Monitore a fila de renderização, workers e histórico de exportações
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="secondary"
            className="flex items-center gap-2 text-xs font-mono"
            onClick={() => {
              fetchJobs()
              fetchHistory()
              fetchBenchmarks()
            }}
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Atualizar</span>
          </Button>
          <Button
            variant="primary"
            className="flex items-center gap-2 text-xs font-mono"
            onClick={() => setIsEnqueueOpen(true)}
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Adicionar Fila</span>
          </Button>
        </div>
      </div>

      {/* Engine Telemetry Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 xl:grid-cols-7 gap-4 shrink-0">
        <Card className="p-4 bg-cyber-bg/30">
          <div className="flex items-center gap-3">
            <PlayCircle className="w-8 h-8 text-neon-green" />
            <div>
              <span className="text-[10px] font-mono text-gray-500 uppercase block">
                Fila Pendente
              </span>
              <span className="text-xl font-bold text-white">{queueSize} Vídeos</span>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-cyber-bg/30">
          <div className="flex items-center gap-3">
            <Cpu className="w-8 h-8 text-neon-cyan" />
            <div>
              <span className="text-[10px] font-mono text-gray-500 uppercase block">
                Workers Ativos
              </span>
              <span className="text-xl font-bold text-white">
                {activeWorkersCount} / {maxWorkers}
              </span>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-cyber-bg/30">
          <div className="flex items-center gap-3">
            <Clock className="w-8 h-8 text-neon-pink" />
            <div>
              <span className="text-[10px] font-mono text-gray-500 uppercase block">
                Prioridade Motor
              </span>
              <span className="text-xl font-bold text-white uppercase tracking-wider">
                {processPriority}
              </span>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-cyber-bg/30">
          <div className="flex items-center gap-3">
            <HardDrive className="w-8 h-8 text-neon-green" />
            <div className="flex-1">
              <div className="flex justify-between items-center mb-1">
                <span className="text-[10px] font-mono text-gray-500 uppercase">Uso de CPU</span>
                <span className="text-[10px] font-mono text-white">
                  {hwData?.cpu_percent || 0}%
                </span>
              </div>
              <ProgressBar value={hwData?.cpu_percent || 0} size="sm" color="green" />
            </div>
          </div>
        </Card>

        {/* Module 08: Health Monitor stats */}
        <Card className="p-4 bg-cyber-bg/30">
          <div className="flex items-center gap-3">
            <CheckSquare className="w-8 h-8 text-neon-green" />
            <div>
              <span className="text-[10px] font-mono text-gray-500 uppercase block">
                Vídeos Hoje
              </span>
              <span className="text-xl font-bold text-white">{stats?.processed_today || 0}</span>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-cyber-bg/30">
          <div className="flex items-center gap-3">
            <Gauge className="w-8 h-8 text-neon-cyan" />
            <div>
              <span className="text-[10px] font-mono text-gray-500 uppercase block">
                Tempo Médio / Vídeo
              </span>
              <span className="text-xl font-bold text-white">
                {stats?.avg_video_time ? `${stats.avg_video_time.toFixed(1)}s` : '-'}
              </span>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-cyber-bg/30">
          <div className="flex items-center gap-3">
            <Database className="w-8 h-8 text-neon-pink" />
            <div>
              <span className="text-[10px] font-mono text-gray-500 uppercase block">
                Cache (Hits / Misses)
              </span>
              <span className="text-xl font-bold text-white">
                {stats?.cache_hits || 0} / {stats?.cache_misses || 0}
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* Tabs Selector */}
      <div className="flex border-b border-cyber-border shrink-0 select-none">
        <button
          onClick={() => setActiveTab('queue')}
          className={`px-6 py-2.5 text-xs font-mono font-bold uppercase tracking-wider border-b-2 transition-all ${
            activeTab === 'queue'
              ? 'border-neon-green text-neon-green'
              : 'border-transparent text-gray-500 hover:text-white'
          }`}
        >
          Fila Geral ({jobs.length})
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`px-6 py-2.5 text-xs font-mono font-bold uppercase tracking-wider border-b-2 transition-all ${
            activeTab === 'history'
              ? 'border-neon-green text-neon-green'
              : 'border-transparent text-gray-500 hover:text-white'
          }`}
        >
          Histórico ({history.length})
        </button>
        <button
          onClick={() => setActiveTab('benchmark')}
          className={`px-6 py-2.5 text-xs font-mono font-bold uppercase tracking-wider border-b-2 transition-all ${
            activeTab === 'benchmark'
              ? 'border-neon-green text-neon-green'
              : 'border-transparent text-gray-500 hover:text-white'
          }`}
        >
          Benchmarks / Métricas
        </button>
      </div>

      {/* Dynamic Content Panel */}
      <div className="flex-1 min-h-0 overflow-y-auto pr-1">
        {activeTab === 'queue' ? (
          <div className="space-y-6">
            {/* Worker Monitor - Card Row */}
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest font-mono">
                Monitor de Workers (Threads de Renderização)
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Array.from({ length: maxWorkers }).map((_, idx) => {
                  const workerIndex = idx
                  const activeJob = runningJobsList[workerIndex]

                  return (
                    <Card
                      key={workerIndex}
                      className={`p-4 border ${
                        activeJob
                          ? activeJob.status === 'paused'
                            ? 'border-yellow-500/30 bg-yellow-500/5'
                            : 'border-neon-green/30 bg-neon-green/5'
                          : 'border-cyber-border/40 bg-cyber-bg/10'
                      }`}
                    >
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-xs font-bold font-mono text-white">
                          Worker #{workerIndex + 1}
                        </span>
                        <span
                          className={`text-[9px] font-mono uppercase px-2 py-0.5 rounded border ${
                            activeJob
                              ? activeJob.status === 'paused'
                                ? 'bg-yellow-500/10 border-yellow-500/20 text-yellow-500'
                                : 'bg-neon-green/10 border-neon-green/20 text-neon-green'
                              : 'bg-cyber-border/40 border-cyber-border text-gray-500'
                          }`}
                        >
                          {activeJob
                            ? activeJob.status === 'paused'
                              ? 'SUSPENSO'
                              : 'EXECUTANDO'
                            : 'OCIOSO'}
                        </span>
                      </div>

                      {activeJob ? (
                        <div className="space-y-3 font-mono text-xs text-gray-400">
                          <div className="truncate">
                            <span className="text-gray-500">Vídeo:</span>{' '}
                            <strong className="text-white">
                              {(activeJob as any).video_name ||
                                (activeJob as any).video?.name ||
                                'Desconhecido'}
                            </strong>
                          </div>

                          <div className="grid grid-cols-2 gap-2 text-[10px]">
                            <div>
                              <span className="text-gray-500">Velocidade:</span>{' '}
                              <strong className="text-neon-cyan">
                                {activeJob.speed?.toFixed(1) || '0.0'}x
                              </strong>
                            </div>
                            <div>
                              <span className="text-gray-500">Tempo Restante:</span>{' '}
                              <strong className="text-white">
                                {activeJob.estimated_time
                                  ? formatDuration(activeJob.estimated_time)
                                  : 'calculando...'}
                              </strong>
                            </div>
                          </div>

                          <div className="space-y-1.5">
                            <div className="flex justify-between text-[10px]">
                              <span>Progresso real</span>
                              <span className="text-neon-green font-bold">
                                {Math.round(activeJob.progress)}%
                              </span>
                            </div>
                            <ProgressBar value={activeJob.progress} size="sm" color="green" />
                          </div>

                          <div className="flex justify-end gap-2 pt-1.5">
                            {activeJob.status === 'paused' ? (
                              <button
                                onClick={() => handleResume(activeJob.id)}
                                className="text-[10px] text-neon-green hover:underline"
                              >
                                Retomar
                              </button>
                            ) : (
                              <button
                                onClick={() => handlePause(activeJob.id)}
                                className="text-[10px] text-yellow-500 hover:underline"
                              >
                                Pausar
                              </button>
                            )}
                            <button
                              onClick={() => handleCancel(activeJob.id)}
                              className="text-[10px] text-neon-pink hover:underline"
                            >
                              Cancelar
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="h-24 flex items-center justify-center text-xs font-mono text-gray-600">
                          Aguardando distribuição de jobs...
                        </div>
                      )}
                    </Card>
                  )
                })}
              </div>
            </div>

            {/* General Queue Table */}
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest font-mono">
                Fila de Processamento
              </h3>

              {jobs.length === 0 ? (
                <div className="border border-dashed border-cyber-border/40 rounded p-12 text-center bg-cyber-bg/10">
                  <Sliders className="w-12 h-12 text-gray-600 mb-4 mx-auto" />
                  <p className="text-sm text-gray-400">Nenhum job na fila do projeto.</p>
                </div>
              ) : (
                <Card className="h-[400px]">
                  <TableVirtuoso
                    data={displayJobs}
                    className="h-full w-full custom-scrollbar"
                    components={{
                      Table: (props) => (
                        <table className="w-full text-left border-collapse text-sm" {...props} />
                      ),
                      TableHead: React.forwardRef((props, ref) => (
                        <thead
                          className="bg-cyber-bg/60 select-none border-b border-cyber-border"
                          {...props}
                          ref={ref}
                        />
                      )),
                      TableRow: (props) => (
                        <tr
                          className="hover:bg-cyber-surface/30 transition-colors duration-150 border-b border-cyber-border/40"
                          {...props}
                        />
                      )
                    }}
                    fixedHeaderContent={() => (
                      <tr>
                        {['Vídeo', 'Template', 'Progresso', 'Status', 'Ações'].map((h) => (
                          <th
                            key={h}
                            className="py-3.5 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono bg-cyber-bg"
                          >
                            {h}
                          </th>
                        ))}
                      </tr>
                    )}
                    itemContent={(_, job) => (
                      <>
                        <TableCell className="font-semibold text-white">
                          {job.video?.name || job.video_id}
                        </TableCell>
                        <TableCell className="font-mono text-xs text-neon-cyan">
                          {job.template?.name || 'Custom'}
                        </TableCell>
                        <TableCell className="w-48">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-mono text-white min-w-[32px]">
                              {Math.round(job.progress)}%
                            </span>
                            <div className="flex-1">
                              <ProgressBar
                                value={job.progress}
                                size="sm"
                                color={job.status === 'failed' ? 'pink' : 'green'}
                              />
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <span
                            className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border ${
                              job.status === 'completed'
                                ? 'bg-neon-green/10 border-neon-green/20 text-neon-green'
                                : job.status === 'failed'
                                  ? 'bg-neon-pink/10 border-neon-pink/20 text-neon-pink'
                                  : job.status === 'running'
                                    ? 'bg-neon-cyan/10 border-neon-cyan/20 text-neon-cyan'
                                    : job.status === 'paused'
                                      ? 'bg-yellow-500/10 border-yellow-500/20 text-yellow-500'
                                      : 'bg-cyber-border/40 border-cyber-border text-gray-400'
                            }`}
                          >
                            {job.status === 'pending'
                              ? 'Fila'
                              : job.status === 'running'
                                ? 'Executando'
                                : job.status === 'completed'
                                  ? 'Concluído'
                                  : job.status === 'failed'
                                    ? 'Erro'
                                    : job.status === 'paused'
                                      ? 'Pausado'
                                      : 'Cancelado'}
                          </span>
                        </TableCell>
                        <TableCell className="space-x-2.5">
                          {job.status === 'paused' && (
                            <button
                              onClick={() => handleResume(job.id)}
                              className="text-xs text-neon-green hover:underline"
                            >
                              Retomar
                            </button>
                          )}
                          {job.status === 'running' && (
                            <button
                              onClick={() => handlePause(job.id)}
                              className="text-xs text-yellow-500 hover:underline"
                            >
                              Pausar
                            </button>
                          )}
                          {job.status === 'failed' && (
                            <button
                              onClick={() => handleReprocess(job.id)}
                              className="text-xs text-neon-green hover:underline"
                            >
                              Reprocessar
                            </button>
                          )}
                          {['pending', 'running', 'paused'].includes(job.status) && (
                            <button
                              onClick={() => handleCancel(job.id)}
                              className="text-xs text-neon-pink hover:underline"
                            >
                              Cancelar
                            </button>
                          )}
                        </TableCell>
                      </>
                    )}
                  />
                </Card>
              )}
            </div>
          </div>
        ) : activeTab === 'history' ? (
          /* History logs view */
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest font-mono">
                Histórico de Exportação
              </h3>
              {history.length > 0 && (
                <Button
                  variant="secondary"
                  size="sm"
                  className="hover:bg-neon-pink/15 text-neon-pink border-neon-pink/20"
                  onClick={handleClearHistory}
                >
                  Limpar Histórico
                </Button>
              )}
            </div>

            {history.length === 0 ? (
              <div className="border border-dashed border-cyber-border/40 rounded p-12 text-center bg-cyber-bg/10">
                <History className="w-12 h-12 text-gray-600 mb-4 mx-auto" />
                <p className="text-sm text-gray-400">
                  Nenhum histórico disponível para este projeto.
                </p>
              </div>
            ) : (
              <Card className="h-[400px]">
                <TableVirtuoso
                  data={history}
                  className="h-full w-full custom-scrollbar"
                  components={{
                    Table: (props) => (
                      <table className="w-full text-left border-collapse text-sm" {...props} />
                    ),
                    TableHead: React.forwardRef((props, ref) => (
                      <thead
                        className="bg-cyber-bg/60 select-none border-b border-cyber-border"
                        {...props}
                        ref={ref}
                      />
                    )),
                    TableRow: (props) => (
                      <tr
                        className="hover:bg-cyber-surface/30 transition-colors duration-150 border-b border-cyber-border/40"
                        {...props}
                      />
                    )
                  }}
                  fixedHeaderContent={() => (
                    <tr>
                      {['Vídeo', 'Template', 'Data Processamento', 'Tempo', 'Resultado', 'Log'].map(
                        (h) => (
                          <th
                            key={h}
                            className="py-3.5 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono bg-cyber-bg"
                          >
                            {h}
                          </th>
                        )
                      )}
                    </tr>
                  )}
                  itemContent={(_, record) => (
                    <>
                      <TableCell className="font-semibold text-white truncate max-w-[150px]">
                        {record.video_name}
                      </TableCell>
                      <TableCell className="text-xs font-mono text-neon-cyan">
                        {record.template_name}
                      </TableCell>
                      <TableCell className="text-xs text-gray-400 font-mono">
                        {formatDate(record.processed_at)}
                      </TableCell>
                      <TableCell className="text-xs text-gray-400 font-mono">
                        {record.execution_time.toFixed(1)}s
                      </TableCell>
                      <TableCell>
                        <span
                          className={`text-[9px] font-mono uppercase px-2 py-0.5 rounded ${
                            record.status === 'completed'
                              ? 'bg-neon-green/10 border border-neon-green/20 text-neon-green'
                              : 'bg-neon-pink/10 border border-neon-pink/20 text-neon-pink'
                          }`}
                        >
                          {record.status === 'completed' ? 'Sucesso' : 'Falha'}
                        </span>
                      </TableCell>
                      <TableCell>
                        <button
                          onClick={() => setSelectedHistory(record)}
                          className="text-xs font-mono text-neon-green flex items-center gap-1 hover:underline"
                        >
                          <Terminal className="w-3.5 h-3.5" /> Ver Log
                        </button>
                      </TableCell>
                    </>
                  )}
                />
              </Card>
            )}
          </div>
        ) : (
          /* Benchmark and Metrics dashboard view */
          <div className="space-y-6">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest font-mono">
              MetricsEngine - Relatório de Benchmarks
            </h3>

            {benchmarks ? (
              <div className="space-y-6">
                {/* Benchmark Metrics Grid */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <Card className="p-4 bg-cyber-bg/20 border-cyber-border/40">
                    <span className="text-[10px] text-gray-500 uppercase font-mono block">
                      Velocidade Média
                    </span>
                    <span className="text-2xl font-bold text-neon-cyan mt-1 block">
                      {benchmarks.avg_speed.toFixed(1)}x
                    </span>
                  </Card>
                  <Card className="p-4 bg-cyber-bg/20 border-cyber-border/40">
                    <span className="text-[10px] text-gray-500 uppercase font-mono block">
                      Tempo Médio Render
                    </span>
                    <span className="text-2xl font-bold text-white mt-1 block">
                      {benchmarks.avg_render_time.toFixed(1)}s
                    </span>
                  </Card>
                  <Card className="p-4 bg-cyber-bg/20 border-cyber-border/40">
                    <span className="text-[10px] text-gray-500 uppercase font-mono block">
                      Taxa de Sucesso
                    </span>
                    <span className="text-2xl font-bold text-neon-green mt-1 block flex items-center gap-1.5">
                      <CheckCircle className="w-5 h-5 text-neon-green" /> {benchmarks.success_rate}%
                    </span>
                  </Card>
                  <Card className="p-4 bg-cyber-bg/20 border-cyber-border/40">
                    <span className="text-[10px] text-gray-500 uppercase font-mono block">
                      Taxa de Erro
                    </span>
                    <span className="text-2xl font-bold text-neon-pink mt-1 block flex items-center gap-1.5">
                      <AlertTriangle className="w-5 h-5 text-neon-pink" /> {benchmarks.error_rate}%
                    </span>
                  </Card>
                </div>

                {/* Resource Metrics Card */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-xs font-bold font-mono text-white tracking-wide uppercase flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-neon-green" />
                      <span>Consumo Médio de Hardware (Durante Renders)</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <div className="flex justify-between text-xs font-mono text-gray-400">
                        <span>Média de CPU</span>
                        <span className="text-white font-bold">
                          {benchmarks.avg_cpu_usage.toFixed(1)}%
                        </span>
                      </div>
                      <ProgressBar value={benchmarks.avg_cpu_usage} size="sm" color="green" />
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between text-xs font-mono text-gray-400">
                        <span>Média de RAM</span>
                        <span className="text-white font-bold">
                          {benchmarks.avg_ram_usage.toFixed(1)}%
                        </span>
                      </div>
                      <ProgressBar value={benchmarks.avg_ram_usage} size="sm" color="cyan" />
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between text-xs font-mono text-gray-400">
                        <span>Média de GPU</span>
                        <span className="text-white font-bold">
                          {benchmarks.avg_gpu_usage.toFixed(1)}%
                        </span>
                      </div>
                      <ProgressBar value={benchmarks.avg_gpu_usage} size="sm" color="pink" />
                    </div>
                  </CardContent>
                </Card>

                {/* Node average times */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-xs font-bold font-mono text-white tracking-wide uppercase">
                      Tempo Médio por Etapa de Processamento (Nodes)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {Object.entries(benchmarks.node_averages).map(([node, timeSec]) => (
                        <div
                          key={node}
                          className="p-3 bg-cyber-bg/40 border border-cyber-border/30 rounded font-mono text-xs"
                        >
                          <span className="text-gray-500 uppercase block">{node}</span>
                          <span className="text-white font-bold mt-1 block">
                            {timeSec > 0 ? `${timeSec.toFixed(2)}s` : '-'}
                          </span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <div className="border border-dashed border-cyber-border/40 rounded p-12 text-center bg-cyber-bg/10">
                <BarChart3 className="w-12 h-12 text-gray-600 mb-4 mx-auto" />
                <p className="text-sm text-gray-400">
                  Aguarde a finalização dos jobs para compilar benchmarks.
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Recovery Prompt Modal */}
      {showRecoveryPrompt && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <Card className="w-full max-w-md border border-neon-cyan">
            <CardHeader className="flex flex-row justify-between items-center pb-2">
              <CardTitle className="text-sm font-semibold tracking-wider text-neon-cyan flex items-center gap-2 uppercase">
                <AlertTriangle className="w-4 h-4 text-neon-cyan" /> Recuperação de Processamento
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-300">
                Foi encontrado um processamento interrompido de uma sessão anterior (
                {interruptedJobs.length} job(s)). O que deseja fazer?
              </p>
              <div className="flex flex-col gap-2 pt-2">
                <Button variant="primary" onClick={() => handleRecoveryAction('continue')}>
                  Continuar (Retomar do Progresso Atual)
                </Button>
                <Button
                  variant="secondary"
                  className="hover:text-neon-cyan"
                  onClick={() => handleRecoveryAction('restart')}
                >
                  Reiniciar do Zero
                </Button>
                <Button
                  variant="secondary"
                  className="hover:text-neon-pink"
                  onClick={() => handleRecoveryAction('cancel')}
                >
                  Cancelar Jobs
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Enqueue Modal */}
      {isEnqueueOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <Card className="w-full max-w-md border border-cyber-border">
            <CardHeader className="flex flex-row justify-between items-center pb-2">
              <CardTitle className="text-sm font-semibold tracking-wider text-neon-cyan flex items-center gap-2 uppercase">
                <Play className="w-4 h-4 text-neon-cyan" /> Batch Process (Fila)
              </CardTitle>
              <button
                onClick={() => setIsEnqueueOpen(false)}
                className="text-gray-500 hover:text-white"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleEnqueue} className="space-y-4">
                <div className="flex flex-col gap-1.5 w-full">
                  <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">
                    Vídeos ({enqueueVideoIds.length} selecionados)
                  </label>
                  {projectVideos.length === 0 ? (
                    <span className="text-xs text-neon-pink">
                      Importe vídeos na biblioteca primeiro.
                    </span>
                  ) : (
                    <div className="max-h-40 overflow-y-auto bg-cyber-bg border border-cyber-border rounded p-2 space-y-1">
                      {projectVideos.map((v) => (
                        <label
                          key={v.id}
                          className="flex items-center gap-2 text-sm text-white cursor-pointer hover:bg-white/5 p-1 rounded"
                        >
                          <input
                            type="checkbox"
                            checked={enqueueVideoIds.includes(v.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setEnqueueVideoIds((prev) => [...prev, v.id])
                              } else {
                                setEnqueueVideoIds((prev) => prev.filter((id) => id !== v.id))
                              }
                            }}
                            className="accent-neon-green"
                          />
                          <span className="truncate">{v.name}</span>
                        </label>
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex flex-col gap-1.5 w-full">
                  <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">
                    Template de Edição
                  </label>
                  {templates.length === 0 ? (
                    <span className="text-xs text-neon-pink">
                      Crie templates na tela de Templates primeiro.
                    </span>
                  ) : (
                    <select
                      value={enqueueTemplateId}
                      onChange={(e) => setEnqueueTemplateId(e.target.value)}
                      className="w-full bg-cyber-bg border border-cyber-border text-sm text-white rounded p-2 outline-none"
                    >
                      {templates.map((t) => (
                        <option key={t.id} value={t.id}>
                          {t.name}
                        </option>
                      ))}
                    </select>
                  )}
                </div>

                <div className="flex flex-col gap-1.5 w-full">
                  <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">
                    Perfil de Exportação
                  </label>
                  {exportProfiles.length === 0 ? (
                    <span className="text-xs text-neon-pink">
                      Crie perfis na tela de Exportação primeiro.
                    </span>
                  ) : (
                    <select
                      value={enqueueExportProfileId}
                      onChange={(e) => setEnqueueExportProfileId(e.target.value)}
                      className="w-full bg-cyber-bg border border-cyber-border text-sm text-white rounded p-2 outline-none"
                    >
                      {exportProfiles.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.name} ({p.resolution})
                        </option>
                      ))}
                    </select>
                  )}
                </div>

                <div className="flex justify-end gap-3 pt-3">
                  <Button type="button" variant="secondary" onClick={() => setIsEnqueueOpen(false)}>
                    Cancelar
                  </Button>
                  <Button
                    type="submit"
                    variant="primary"
                    disabled={
                      enqueueVideoIds.length === 0 ||
                      templates.length === 0 ||
                      exportProfiles.length === 0
                    }
                  >
                    Processar
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Log Details Modal */}
      {selectedHistory && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <Card className="w-full max-w-2xl border border-cyber-border">
            <CardHeader className="flex flex-row justify-between items-center pb-2">
              <CardTitle className="text-sm font-semibold tracking-wider text-neon-cyan flex items-center gap-2 uppercase">
                <Terminal className="w-4 h-4 text-neon-cyan" /> Relatório de Renderização
              </CardTitle>
              <button
                onClick={() => setSelectedHistory(null)}
                className="text-gray-500 hover:text-white"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-xs font-mono border-b border-cyber-border/40 pb-3">
                <div>
                  <span className="text-gray-500 block uppercase">Vídeo</span>
                  <span className="text-white font-semibold">{selectedHistory.video_name}</span>
                </div>
                <div>
                  <span className="text-gray-500 block uppercase">Template Utilizado</span>
                  <span className="text-neon-cyan">{selectedHistory.template_name}</span>
                </div>
                <div>
                  <span className="text-gray-500 block uppercase">Data de Finalização</span>
                  <span className="text-white">{formatDate(selectedHistory.processed_at)}</span>
                </div>
                <div>
                  <span className="text-gray-500 block uppercase">Tempo Processamento</span>
                  <span className="text-white">
                    {selectedHistory.execution_time.toFixed(1)} segundos
                  </span>
                </div>
              </div>

              <div className="flex flex-col gap-1.5">
                <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">
                  Logs do Pipeline de Nodes
                </span>
                <pre className="bg-black/60 border border-cyber-border/40 p-4 rounded text-xs text-neon-green font-mono overflow-auto max-h-[300px] leading-relaxed">
                  {selectedHistory.log || 'Nenhum log gravado.'}
                </pre>
              </div>

              {selectedHistory.exported_path && (
                <div className="text-xs font-mono bg-cyber-bg/40 border border-cyber-border/30 rounded p-3 text-gray-400 truncate">
                  <span className="text-[10px] text-gray-500 uppercase block mb-1">
                    Caminho do Vídeo Exportado
                  </span>
                  <span className="text-neon-green font-semibold">
                    {selectedHistory.exported_path}
                  </span>
                </div>
              )}

              <div className="flex justify-end pt-2">
                <Button variant="secondary" onClick={() => setSelectedHistory(null)}>
                  Fechar
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
