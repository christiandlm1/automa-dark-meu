import React, { createContext, useContext, useState, useCallback } from 'react'

export type ToastType = 'success' | 'info' | 'warning' | 'error'

export interface ToastMessage {
  id: string
  message: string
  type: ToastType
  duration?: number
}

interface ToastContextType {
  toasts: ToastMessage[]
  showToast: (message: any, type: ToastType, duration?: number) => void
  removeToast: (id: string) => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastMessage[]>([])

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }, [])

  const showToast = useCallback(
    (message: any, type: ToastType, duration = 4000) => {
      let msgStr = 'Ocorreu um alerta'
      if (typeof message === 'string') {
        msgStr = message
      } else if (message instanceof Error) {
        msgStr = message.message
      } else if (typeof message === 'object' && message !== null) {
        msgStr = message.message || message.detail || JSON.stringify(message)
      } else {
        msgStr = String(message)
      }

      const id = Math.random().toString(36).substring(2, 9)
      setToasts((prev) => [...prev, { id, message: msgStr, type, duration }])

      if (duration > 0) {
        setTimeout(() => {
          removeToast(id)
        }, duration)
      }
    },
    [removeToast]
  )

  return (
    <ToastContext.Provider value={{ toasts, showToast, removeToast }}>
      {children}
    </ToastContext.Provider>
  )
}

export const useToast = () => {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}
