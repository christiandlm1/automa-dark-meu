import React from 'react'
import { Sidebar } from './Sidebar'
import { Navbar } from './Navbar'
import { useToast } from '../../contexts/ToastContext'
import { AlertCircle, CheckCircle2, Info, AlertTriangle, X } from 'lucide-react'
import { api } from '../../services/api'
import { FirstUseWizard } from '../wizard/FirstUseWizard'

export const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [showWizard, setShowWizard] = React.useState(false)
  const { toasts, removeToast } = useToast()

  React.useEffect(() => {
    api.get<any>('/settings/key/first_run_completed').then(res => {
      if ((res?.data?.value || res?.value) === 'false') setShowWizard(true)
    }).catch(() => {})
  }, [])

  const toastIcons = {
    success: <CheckCircle2 className="w-5 h-5 text-neon-green" />,
    info: <Info className="w-5 h-5 text-neon-cyan" />,
    warning: <AlertTriangle className="w-5 h-5 text-neon-yellow" />,
    error: <AlertCircle className="w-5 h-5 text-neon-pink" />
  }

  const toastBorderColors = {
    success: 'border-neon-green/50 shadow-neon-green/10',
    info: 'border-neon-cyan/50 shadow-neon-cyan/10',
    warning: 'border-neon-yellow/50 shadow-neon-yellow/10',
    error: 'border-neon-pink/50 shadow-neon-pink/10'
  }

  return (
    <div className="flex w-screen h-screen bg-cyber-bg overflow-hidden text-gray-200">
      {/* Side Navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        {/* Top Navbar */}
        <Navbar />

        {/* Dynamic Route Content */}
        <main className="flex-1 overflow-y-auto p-8 cyber-grid-bg relative">{children}</main>
      </div>

      {/* Floating Cyberpunk Toast Notifications */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3 max-w-sm w-full pointer-events-none">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`pointer-events-auto p-4 rounded-lg border bg-cyber-panel/95 backdrop-blur-md shadow-lg flex gap-3 items-start justify-between transform transition-all duration-300 animate-slide-in ${
              toastBorderColors[toast.type]
            }`}
          >
            <div className="shrink-0 pt-0.5">{toastIcons[toast.type]}</div>
            <div className="flex-1 text-sm font-medium text-white break-words pr-2">
              {toast.message}
            </div>
            <button
              onClick={() => removeToast(toast.id)}
              className="text-gray-500 hover:text-white transition-colors shrink-0"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
      {showWizard && <FirstUseWizard onComplete={() => setShowWizard(false)} />}
    </div>
  )
}
