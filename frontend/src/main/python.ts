import { spawn, ChildProcess } from 'child_process'
import path from 'path'
import { app } from 'electron'

let pythonProcess: ChildProcess | null = null
const BACKEND_PORT = 8420

export function getBackendUrl(): string {
  return `http://127.0.0.1:${BACKEND_PORT}`
}

/**
 * Polls GET /health until the backend answers, so the window is only opened once the
 * API can serve requests. Resolves true when healthy, false if the timeout is reached.
 */
export async function waitForBackend(timeoutMs = 30000, intervalMs = 300): Promise<boolean> {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    try {
      const res = await fetch(`${getBackendUrl()}/health`, { signal: AbortSignal.timeout(1000) })
      if (res.ok) return true
    } catch {
      // Backend is not accepting connections yet; retry below.
    }
    await new Promise((resolve) => setTimeout(resolve, intervalMs))
  }
  return false
}

export function startPythonBackend(): void {
  const isDev = !app.isPackaged
  let executablePath = 'python'
  let args: string[] = []
  let cwd: string | undefined = undefined

  if (isDev) {
    // Development Mode
    cwd = path.join(app.getAppPath(), '../backend')
    executablePath = path.join(cwd, '.venv', 'Scripts', 'python.exe')
    args = ['main.py']
    console.log(`[Python Manager] Starting in DEV mode: ${executablePath} main.py inside ${cwd}`)
  } else {
    // Packaged Production Mode
    executablePath = path.join(process.resourcesPath, 'backend', 'api-server.exe')
    cwd = undefined
    console.log(`[Python Manager] Starting in PROD mode: ${executablePath}`)
  }

  try {
    pythonProcess = spawn(executablePath, args, {
      cwd,
      stdio: ['ignore', 'pipe', 'pipe'],
      windowsHide: true
    })

    pythonProcess.stdout?.on('data', (data) => {
      console.log(`[Python Stdout] ${data.toString().trim()}`)
    })

    pythonProcess.stderr?.on('data', (data) => {
      console.error(`[Python Stderr] ${data.toString().trim()}`)
    })

    pythonProcess.on('close', (code) => {
      console.log(`[Python Manager] Process exited with code ${code}`)
      pythonProcess = null
    })

    pythonProcess.on('error', (err) => {
      console.error('[Python Manager] Failed to start subprocess:', err)
    })
  } catch (err) {
    console.error('[Python Manager] Error spawning Python backend:', err)
  }
}

export function stopPythonBackend(): void {
  if (pythonProcess) {
    console.log('[Python Manager] Stopping Python backend process...')
    if (process.platform === 'win32') {
      // Force kill the process tree on Windows
      spawn('taskkill', ['/pid', String(pythonProcess.pid), '/f', '/t'])
    } else {
      pythonProcess.kill('SIGTERM')
    }
    pythonProcess = null
  }
}
