import { ArrowUpRight } from 'lucide-react'
import type { Catalog, Experiment, Technology } from '../../shared/contracts'
import { formatDate, formatNumber } from '../../shared/format'

const statusLabels: Record<Experiment['status'], string> = {
  queued: 'En cola',
  running: 'En ejecución',
  succeeded: 'Completada',
  failed: 'Fallida',
  interrupted: 'Interrumpida',
}

export function HistoryPanel({
  experiments,
  technologies,
  designs,
  selectedId,
  onSelect,
}: {
  experiments: Experiment[]
  technologies: Technology[]
  designs: Catalog['designs']
  selectedId?: string
  onSelect: (id: string) => void
}) {
  return (
    <section className="panel history-panel" aria-labelledby="history-title">
      <div className="section-heading">
        <div>
          <h2 id="history-title">Historial de evaluaciones</h2>
          <p>Configuraciones y resultados guardados localmente.</p>
        </div>
        <span className="count-badge">{experiments.length}</span>
      </div>
      {experiments.length === 0 ? (
        <p className="history-empty">Todavía no hay evaluaciones.</p>
      ) : (
        <div className="table-scroll">
          <table>
            <caption className="sr-only">Historial de síntesis por DPU y tecnología</caption>
            <thead>
              <tr>
                <th>Evaluación</th>
                <th>Tecnología</th>
                <th>Estado</th>
                <th>Área total</th>
                <th>
                  <span className="sr-only">Abrir resultado</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {experiments.map((item) => (
                <tr key={item.id} className={item.id === selectedId ? 'selected-row' : ''}>
                  <td>
                    <strong>
                      {item.report?.numeric_format ??
                        designs.find((design) => design.id === item.design_id)?.numeric_format ??
                        item.design_id}
                    </strong>
                    <small>{formatDate(item.created_at)}</small>
                  </td>
                  <td>
                    {technologies.find((tech) => tech.id === item.technology_id)?.label ??
                      item.technology_id}
                  </td>
                  <td>
                    <span className={`badge ${item.status}`}>{statusLabels[item.status]}</span>
                  </td>
                  <td className="numeric">
                    {item.report ? `${formatNumber(item.report.total_area)} µm²` : '—'}
                  </td>
                  <td>
                    <button
                      className="icon-button"
                      aria-label={`Ver evaluación ${item.id}`}
                      onClick={() => onSelect(item.id)}
                    >
                      <ArrowUpRight size={18} aria-hidden="true" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
