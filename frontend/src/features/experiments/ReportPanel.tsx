import { CheckCircle2, Download, FileJson, Layers3, LoaderCircle } from 'lucide-react'
import type { Experiment } from '../../shared/contracts'
import { apiUrl } from '../../shared/api'
import { formatNumber } from '../../shared/format'
import { PipelineSteps } from './PipelineSteps'

export function ReportPanel({ experiment }: { experiment?: Experiment }) {
  const report = experiment?.report
  const active = experiment && ['queued', 'running'].includes(experiment.status)
  return (
    <section className="panel report-panel" aria-labelledby="report-title" aria-live="polite">
      <div className="panel-heading">
        <span className="step-number">02</span>
        <div>
          <h2 id="report-title">Resultado de síntesis</h2>
          <p>
            {report
              ? `${report.numeric_format} · ${report.technology_label} · ${report.node_nm} nm · ${report.corner}`
              : 'Área obtenida de las celdas mapeadas.'}
          </p>
        </div>
        {report && (
          <span className="badge success">
            <CheckCircle2 size={13} aria-hidden="true" />
            Validado
          </span>
        )}
      </div>
      <PipelineSteps experiment={experiment} />
      {!experiment && (
        <div className="empty-state">
          <div className="empty-icon">
            <Layers3 size={31} aria-hidden="true" />
          </div>
          <h3>Tu primera medición empieza aquí</h3>
          <p>
            Selecciona una DPU y una tecnología para calcular el área.
            <br />
            Los resultados aparecerán cuando finalice la validación.
          </p>
          <span className="empty-formula">R = Σ Aᵢ × Bᵢ + C₀</span>
        </div>
      )}
      {active && (
        <div className="empty-state">
          <LoaderCircle className="spin" size={30} aria-hidden="true" />
          <h3>
            {experiment.status === 'queued'
              ? 'Evaluación en cola'
              : `Evaluando la DPU ${experiment.design_id.toUpperCase()}`}
          </h3>
          <p>
            La evaluación continúa aunque cierres esta pestaña.
            <br />
            El estado se actualiza automáticamente.
          </p>
        </div>
      )}
      {experiment && ['failed', 'interrupted'].includes(experiment.status) && (
        <div className="error-state" role="alert">
          <h3>La evaluación no produjo un área válida</h3>
          <p>{experiment.error}</p>
          <p>Consulta los logs para identificar la etapa que falló.</p>
        </div>
      )}
      {report && (
        <>
          <div className="area-hero">
            <span className="eyebrow">ÁREA TOTAL DE CELDAS</span>
            <div>
              <strong>{formatNumber(report.total_area)}</strong>
              <span>µm²</span>
            </div>
            <p>
              {formatNumber(report.total_cells, 0)} celdas ·{' '}
              {formatNumber(report.duration_seconds, 1)} segundos
            </p>
          </div>
          <div className="area-breakdown">
            <div>
              <span>
                <i className="dot combinational" />
                Lógica combinacional
              </span>
              <strong>
                {formatNumber(report.combinational_area)} <small>µm²</small>
              </strong>
            </div>
            <div>
              <span>
                <i className="dot sequential" />
                Estado secuencial
              </span>
              <strong>
                {formatNumber(report.sequential_area)} <small>µm²</small>
              </strong>
            </div>
            <div>
              <span>Flip-flops / latches</span>
              <strong>
                {report.cell_counts.flip_flop} / {report.cell_counts.latch}
              </strong>
            </div>
          </div>
          <div className="validation-note">
            <CheckCircle2 size={17} aria-hidden="true" />
            <span>
              RTL y netlist: <strong>{report.validation.vectors} vectores aprobados</strong>.
              {report.validation.reference === 'rtl_bit_exact'
                ? ' Comparación bit a bit con el RTL original; precisión numérica no evaluada.'
                : ' Incluye referencia entera independiente con signo y overflow.'}
            </span>
          </div>
          <div className="downloads">
            <a
              className="button secondary"
              href={apiUrl(`/api/v1/experiments/${experiment.id}/artifacts`)}
            >
              <Download size={15} aria-hidden="true" />
              Artefactos ZIP
            </a>
            <a
              className="button text-button"
              href={apiUrl(`/api/v1/experiments/${experiment.id}/report.csv`)}
            >
              <FileJson size={15} aria-hidden="true" />
              Desglose CSV
            </a>
          </div>
          <details className="provenance">
            <summary>Trazabilidad y alcance</summary>
            <dl>
              <dt>Top</dt>
              <dd>{report.top}</dd>
              <dt>Liberty SHA-256</dt>
              <dd>{report.manifest.liberty_sha256}</dd>
              <dt>Mapeo</dt>
              <dd>{report.manifest.mapping_policy}</dd>
              <dt>Unidades</dt>
              <dd>{report.area_unit_basis}</dd>
              <dt>Verificaciones</dt>
              <dd>Pruebas funcionales por vectores; equivalencia formal y timing no ejecutados.</dd>
            </dl>
          </details>
        </>
      )}
    </section>
  )
}
