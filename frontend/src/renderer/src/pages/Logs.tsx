import React, { useState, useEffect } from 'react'
import { useProject } from '../contexts/ProjectContext'
import { logService } from '../services/logService'
import { Log } from '../types/log'
import { Table, TableRow, TableCell } from '../components/ui/Table'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Terminal, RefreshCw, AlertCircle, Info } from 'lucide-react'
import { formatDate } from '../utils/format'

export const Logs: React.FC = () => {
  const { activeProject } = useProject()
  const [logs, setLogs] = useState<Log[]>([])
  const [loading, setLoading] = useState(false)
  const [levelFilter, setLevelFilter] = useState('all')

  const fetchLogs = async () => {
    if (!activeProject) return
    setLoading(true)
    try {
      const response = await logService.list(
        0,
        500,
        activeProject.id,
        levelFilter === 'all' ? undefined : levelFilter
      )
      setLogs(response.logs)
    } catch (err) {
      console.error('Failed to fetch logs:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLogs()
  }, [activeProject, levelFilter])

  const levelBadges = {
    info: 'border-neon-cyan/35 text-neon-cyan bg-neon-cyan/5',
    warning: 'border-neon-yellow/35 text-neon-yellow bg-neon-yellow/5',
    error: 'border-neon-pink/35 text-neon-pink bg-neon-pink/5'
  }

  const levelIcons = {
    info: <Info className="w-3.5 h-3.5 text-neon-cyan shrink-0" />,
    warning: <AlertCircle className="w-3.5 h-3.5 text-neon-yellow shrink-0" />,
    error: <AlertCircle className="w-3.5 h-3.5 text-neon-pink shrink-0" />
  }

  return (
    <div className="space-y-6 select-none">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold tracking-wider text-white">
            Registro de Auditoria (Logs)
          </h2>
          <p className="text-xs font-mono text-gray-500 mt-1 uppercase">
            Acompanhe o histórico de todas as ações tomadas pelo usuário ou sistema
          </p>
        </div>
        <button
          onClick={fetchLogs}
          disabled={loading}
          className="p-2 border border-cyber-border rounded-lg bg-cyber-panel/60 text-gray-400 hover:text-white hover:border-gray-500 transition-colors flex items-center gap-1.5 text-xs font-mono"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Atualizar
        </button>
      </div>

      {/* Filter and Content Card */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-4">
          <CardTitle className="flex items-center gap-2">
            <Terminal className="w-5 h-5 text-neon-green" />
            <span>Mensagens do Console</span>
          </CardTitle>

          <select
            value={levelFilter}
            onChange={(e) => setLevelFilter(e.target.value)}
            className="bg-cyber-bg border border-cyber-border focus:border-neon-green/60 text-xs text-gray-300 rounded px-3 py-1.5 outline-none cursor-pointer font-mono"
          >
            <option value="all">Todos Níveis</option>
            <option value="info">Informações</option>
            <option value="warning">Avisos</option>
            <option value="error">Erros</option>
          </select>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center items-center py-16">
              <svg className="animate-spin h-6 w-6 text-neon-green" viewBox="0 0 24 24" fill="none">
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
          ) : logs.length === 0 ? (
            <div className="text-center py-16 font-mono text-xs text-gray-500">
              Nenhum registro encontrado para os filtros selecionados
            </div>
          ) : (
            <Table headers={['Data/Hora', 'Nível', 'Ação', 'Mensagem', 'Detalhes Extra']}>
              {logs.map((log) => (
                <TableRow key={log.id}>
                  {/* Timestamp */}
                  <TableCell className="font-mono text-xs text-gray-400 w-44">
                    {formatDate(log.created_at)}
                  </TableCell>

                  {/* Level Badge */}
                  <TableCell className="w-28">
                    <span
                      className={`px-2 py-0.5 rounded border text-[9px] font-mono font-bold uppercase tracking-wider flex items-center gap-1 w-max ${
                        levelBadges[log.level]
                      }`}
                    >
                      {levelIcons[log.level]}
                      {log.level}
                    </span>
                  </TableCell>

                  {/* Action */}
                  <TableCell className="font-mono text-xs text-white capitalize w-28">
                    {log.action}
                  </TableCell>

                  {/* Message */}
                  <TableCell className="text-gray-300 font-semibold" title={log.message}>
                    {log.message}
                  </TableCell>

                  {/* Extra Details */}
                  <TableCell
                    className="font-mono text-[10px] text-gray-500 max-w-[200px] truncate"
                    title={log.details || ''}
                  >
                    {log.details || '-'}
                  </TableCell>
                </TableRow>
              ))}
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
