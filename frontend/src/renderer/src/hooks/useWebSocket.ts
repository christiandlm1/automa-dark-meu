import { useEffect, useState, useRef, useCallback } from 'react'
import { WS_BASE_URL } from '../services/api'

export function useWebSocket<T>(path: string) {
  const [data, setData] = useState<T | null>(null)
  const [connected, setConnected] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const socketRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<number | null>(null)

  const connect = useCallback(() => {
    if (socketRef.current?.readyState === WebSocket.OPEN) return

    const wsUrl = `${WS_BASE_URL}${path}`
    const socket = new WebSocket(wsUrl)
    socketRef.current = socket

    socket.onopen = () => {
      setConnected(true)
      setError(null)
      console.log(`WebSocket connected: ${wsUrl}`)
    }

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data)
        if (payload && payload.type === 'hardware_telemetry') {
          setData(payload.data)
        } else {
          setData(payload)
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err)
      }
    }

    socket.onerror = (event) => {
      setError('Connection error')
      console.error('WebSocket error:', event)
    }

    socket.onclose = () => {
      setConnected(false)
      console.log(`WebSocket closed: ${wsUrl}`)

      // Attempt reconnection after 3 seconds
      reconnectTimeoutRef.current = window.setTimeout(() => {
        connect()
      }, 3000)
    }
  }, [path])

  useEffect(() => {
    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (socketRef.current) {
        socketRef.current.onclose = null // Prevent reconnect loop
        socketRef.current.close()
      }
    }
  }, [connect])

  return { data, connected, error }
}
