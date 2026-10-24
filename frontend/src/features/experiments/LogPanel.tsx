import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Terminal } from 'lucide-react'
import { api } from '../../shared/api'
import type { Experiment } from '../../shared/contracts'

export function LogPanel({ experiment }: { experiment?: Experiment }) {
  const [open, setOpen] = useState(false)
  const query = useQuery({
    queryKey: ['logs', experiment?.id],
    queryFn: ({ signal }) => api.logs(experiment!.id, signal),
    enabled: open && !!experiment,
    refetchInterval: open && experiment?.status === 'running' ? 2000 : false,
  })
  if (!experiment) return null
  return (
    <section className="panel log-panel">
      <button
        className="log-toggle"
        aria-expanded={open}
        aria-controls="run-log"
        onClick={() => setOpen(!open)}
      >
        <Terminal size={16} aria-hidden="true" />
        <span>Logs de la evaluación</span>
        <span>{open ? 'Ocultar' : 'Mostrar'}</span>
      </button>
      {open && (
        <div id="run-log">
          {query.error && <p role="alert">{query.error.message}</p>}
          {query.data?.truncated && (
            <p className="log-note">
              Se muestran los últimos 100 KB. El ZIP contiene el log completo.
            </p>
          )}
          <pre tabIndex={0}>
            {query.isPending
              ? 'Cargando…'
              : query.data?.content || 'Esperando salida de las herramientas…'}
          </pre>
        </div>
      )}
    </section>
  )
}
