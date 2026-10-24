import { useState } from 'react'
import { Activity, ArrowUpRight, Cpu, FlaskConical, Library, ShieldCheck } from 'lucide-react'
import { useCatalog, useCreateExperiment, useExperiments } from './features/experiments/hooks'
import { ExperimentForm } from './features/experiments/ExperimentForm'
import { ReportPanel } from './features/experiments/ReportPanel'
import { ComparisonPanel } from './features/experiments/ComparisonPanel'
import { HistoryPanel } from './features/experiments/HistoryPanel'
import { LogPanel } from './features/experiments/LogPanel'
import { apiUrl } from './shared/api'

export default function App() {
  const catalog = useCatalog()
  const experiments = useExperiments()
  const create = useCreateExperiment()
  const [selectedId, setSelectedId] = useState<string>()
  const [designId, setDesignId] = useState('int8_16')
  const items = experiments.data ?? []
  const selected =
    items.find((item) => item.id === selectedId) ?? (!selectedId ? items[0] : undefined)
  const runningCount = items.filter((item) => ['running', 'queued'].includes(item.status)).length

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="/" aria-label="ASIC Area Lab, inicio">
          <span className="brand-mark">
            <Cpu size={24} aria-hidden="true" />
          </span>
          <span>
            ASIC<span>AREA LAB</span>
          </span>
        </a>
        <span className="sidebar-label">ESPACIO DE TRABAJO</span>
        <nav aria-label="Navegación principal">
          <a className="nav-link current" href="#workspace">
            <FlaskConical size={18} aria-hidden="true" />
            Evaluaciones
            <span className="nav-dot" />
          </a>
          <a className="nav-link" href="#comparison-title">
            <Activity size={18} aria-hidden="true" />
            Comparación
          </a>
          <a className="nav-link" href={apiUrl('/docs')} target="_blank" rel="noreferrer">
            <Library size={18} aria-hidden="true" />
            Documentación API
            <ArrowUpRight size={14} aria-hidden="true" />
          </a>
        </nav>
        <div className="sidebar-bottom">
          <ShieldCheck size={20} aria-hidden="true" />
          <strong>Resultados reproducibles</strong>
          <p>RTL, biblioteca y versiones registrados en cada evaluación.</p>
          <span>11 FORMATOS DPU · 3 TECNOLOGÍAS</span>
        </div>
      </aside>
      <main id="workspace">
        <header className="topbar">
          <span>
            Laboratorio de síntesis <span className="breadcrumb">/</span> <strong>Área ASIC</strong>
          </span>
          <span className="connection">
            <i />
            {runningCount ? `${runningCount} en proceso` : 'Entorno local'}
          </span>
        </header>
        <div className="content">
          <div className="page-heading">
            <div>
              <span className="eyebrow">DEL VHDL A LAS CELDAS</span>
              <h1>
                El área de tu DPU,
                <br className="mobile-break" /> medida.
              </h1>
              <p>
                Selecciona una DPU del repositorio y compara su área
                <br className="desktop-break" /> al mapearla a distintas tecnologías.
              </p>
            </div>
            <div className="scope-chip">
              <Cpu size={19} aria-hidden="true" />
              <span>
                Medición a nivel de celdas<strong>Sin conexiones ni diseño físico</strong>
              </span>
            </div>
          </div>
          {(catalog.error || experiments.error || create.error) && (
            <div className="alert" role="alert">
              {catalog.error?.message ?? experiments.error?.message ?? create.error?.message}
            </div>
          )}
          {catalog.isPending ? (
            <div className="panel loading">Cargando bibliotecas y diseños…</div>
          ) : (
            catalog.data && (
              <>
                <div className="workspace-grid">
                  <ExperimentForm
                    catalog={catalog.data}
                    pending={create.isPending}
                    designId={designId}
                    onDesignChange={setDesignId}
                    onSubmit={(chosenDesignId, technologyId) =>
                      create.mutate(
                        { designId: chosenDesignId, technologyId },
                        { onSuccess: (item) => setSelectedId(item.id) },
                      )
                    }
                  />
                  <ReportPanel experiment={selected} />
                </div>
                <ComparisonPanel
                  experiments={items}
                  designId={designId}
                  technologies={catalog.data.technologies}
                />
                <HistoryPanel
                  experiments={items}
                  technologies={catalog.data.technologies}
                  designs={catalog.data.designs}
                  selectedId={selected?.id}
                  onSelect={setSelectedId}
                />
                <LogPanel key={selected?.id} experiment={selected} />
              </>
            )
          )}
          <footer>
            <span>ASIC Area Lab</span>
            <span>GHDL → Verilog → Yosys → Liberty → reporte</span>
          </footer>
        </div>
      </main>
    </div>
  )
}
