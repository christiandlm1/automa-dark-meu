import React from 'react'

interface ErrorBoundaryProps {
  children: React.ReactNode
}

interface ErrorBoundaryState {
  error: Error | null
}

/**
 * Catches render errors in a screen so a single bug does not blank the whole app.
 * Shows the error message instead of a black window.
 */
export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  override state: ErrorBoundaryState = { error: null }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error }
  }

  override componentDidCatch(error: Error, info: React.ErrorInfo): void {
    console.error('[ErrorBoundary]', error, info.componentStack)
  }

  override render(): React.ReactNode {
    if (!this.state.error) return this.props.children

    return (
      <div className="p-8 font-mono text-white">
        <h2 className="mb-2 text-lg font-bold text-neon-pink">Algo deu errado nesta tela</h2>
        <p className="mb-2 text-xs text-gray-400">
          O restante do app continua funcionando. Detalhes completos: tecle F12 e abra a aba Console.
        </p>
        <pre className="mb-4 whitespace-pre-wrap rounded border border-cyber-border bg-black/60 p-3 text-xs text-gray-300">
          {this.state.error.message}
        </pre>
        <button
          className="rounded bg-zinc-700 px-4 py-2 text-sm hover:bg-zinc-600"
          onClick={() => this.setState({ error: null })}
        >
          Tentar novamente
        </button>
      </div>
    )
  }
}
