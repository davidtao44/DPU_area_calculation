import { Component, type ErrorInfo, type ReactNode } from 'react'

export class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false }
  static getDerivedStateFromError() {
    return { failed: true }
  }
  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('UI error', error, info.componentStack)
  }
  render() {
    if (this.state.failed)
      return (
        <main className="error-fallback">
          <h1>No se pudo mostrar la aplicación</h1>
          <p>Recarga la página para volver a consultar las evaluaciones.</p>
          <button onClick={() => window.location.reload()}>Recargar</button>
        </main>
      )
    return this.props.children
  }
}
