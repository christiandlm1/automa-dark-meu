import { useEffect, useState, useRef, useCallback } from 'react'
import { WS_BASE_URL } from '../services/api'

export function useWebSocket<T>(path: string) {
  const [data, setData] = useState<T | null>(null)
  const [connected, setConnected] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const socketRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<number | null>(null)
  const disposedRef = useRef<boolean>(false)

  const connect = useCallback(() => {
    if (disposedRef.current) return
    const current = socketRef.current
    if (
      current &&
      (current.readyState === WebSocket.OPEN || current.readyState === WebSocket.CONNECTING)
    ) {
      return
    }

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
        // The backend wraps updates as { type: "..._telemetry", data: {...} }.
        // Consumers expect the inner object (e.g. running_jobs, cpu_percent).
        if (
          payload &&
          typeof payload.type === 'string' &&
          payload.type.endsWith('_telemetry') &&
          'data' in payload
        ) {
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
      if (!disposedRef.current) {
        reconnectTimeoutRef.current = window.setTimeout(() => {
          connect()
        }, 3000)
      }
    }
  }, [path])

  useEffect(() => {
    disposedRef.current = false
    connect()

    return () => {
      disposedRef.current = true
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      const socket = socketRef.current
      if (socket) {
        // Detach every handler so closing a half-open socket (React StrictMode / route
        // changes) does not log fake errors or trigger a reconnect.
        socket.onmessage = null
        socket.onerror = null
        socket.onclose = null
        if (socket.readyState === WebSocket.CONNECTING) {
          // Closing a socket that is still connecting makes the browser print
          // "closed before the connection is established"; wait until it opens instead.
          socket.onopen = () => socket.close()
        } else {
          socket.onopen = null
          socket.close()
        }
        socketRef.current = null
      }
    }
  }, [connect])

  return { data, connected, error }
}
