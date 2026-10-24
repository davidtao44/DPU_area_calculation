import { useState } from 'react'
import type { Experiment, Technology } from '../../shared/contracts'
import { formatNumber } from '../../shared/format'

export function ComparisonPanel({
  experiments,
  designId,
  technologies,
}: {
  experiments: Experiment[]
  designId: string
  technologies: Technology[]
}) {
  const [mode, setMode] = useState('technology')
  const [technologyId, setTechnologyId] = useState(technologies[0]?.id ?? '')
  const unique = new Map<string, Experiment>()
  for (const item of experiments) {
    const matches =
      mode === 'technology' ? item.design_id === designId : item.technology_id === technologyId
    const key = mode === 'technology' ? item.technology_id : item.design_id
    if (matches && item.status === 'succeeded' && item.report) {
      const previous = unique.get(key)
      if (!previous || item.created_at > previous.created_at) unique.set(key, item)
    }
  }
  const items = [...unique.values()].sort((a, b) =>
    mode === 'technology'
      ? (b.report?.node_nm ?? 0) - (a.report?.node_nm ?? 0)
      : a.design_id.localeCompare(b.design_id),
  )
  const maximum = Math.max(1, ...items.map((item) => item.report?.total_area ?? 0))
  return (
    <section className="panel comparison-panel" aria-labelledby="comparison-title">
      <div className="section-heading">
        <div>
          <h2 id="comparison-title">Comparación de área</h2>
          <p>
            {mode === 'technology'
              ? `Última evaluación válida de ${designId.toUpperCase()} por biblioteca.`
              : 'Última evaluación válida de cada formato en la misma biblioteca.'}
          </p>
        </div>
        <div className="legend">
          <span>
            <i className="dot combinational" />
            Lógica
          </span>
          <span>
            <i className="dot sequential" />
            Estado
          </span>
        </div>
      </div>
      <div className="comparison-controls">
        <label>
          Comparar
          <select value={mode} onChange={(event) => setMode(event.target.value)}>
            <option value="technology">Tecnologías para la DPU seleccionada</option>
            <option value="format">Formatos en una tecnología</option>
          </select>
        </label>
        {mode === 'format' && (
          <label>
            Biblioteca de comparación
            <select value={technologyId} onChange={(event) => setTechnologyId(event.target.value)}>
              {technologies.map((tech) => (
                <option key={tech.id} value={tech.id}>
                  {tech.label}
                </option>
              ))}
            </select>
          </label>
        )}
      </div>
      {items.length === 0 ? (
        <div className="comparison-empty">
          Las evaluaciones válidas construirán esta comparación. No se utilizan datos simulados.
        </div>
      ) : (
        <div className="comparison-chart">
          {items.map(
            ({ id, report }) =>
              report && (
                <div className="chart-row" key={id}>
                  <div className="chart-label">
                    <strong>
                      {mode === 'technology' ? `${report.node_nm} nm` : report.numeric_format}
                    </strong>
                    <small>{report.technology_label}</small>
                  </div>
                  <div
                    className="chart-track"
                    role="img"
                    aria-label={`${report.numeric_format}, ${report.technology_label}: ${report.total_area} micrómetros cuadrados`}
                  >
                    <div
                      className="chart-bar combinational"
                      style={{ width: `${(report.combinational_area / maximum) * 100}%` }}
                    />
                    <div
                      className="chart-bar sequential"
                      style={{ width: `${(report.sequential_area / maximum) * 100}%` }}
                    />
                  </div>
                  <strong className="chart-value">
                    {formatNumber(report.total_area)} <small>µm²</small>
                  </strong>
                </div>
              ),
          )}
          <p className="chart-footnote">
            {mode === 'technology'
              ? 'Misma DPU y política de síntesis. Cada tecnología usa su condición nominal.'
              : 'Distintos circuitos y precisiones con la misma biblioteca y política de síntesis.'}{' '}
            Incluye el wrapper registrado. No es una comparación de frecuencia ni precisión
            numérica.
          </p>
        </div>
      )}
    </section>
  )
}
