import { useState } from 'react'
import { ArrowRight, Check, CircleDashed } from 'lucide-react'
import type { Catalog } from '../../shared/contracts'

interface Props {
  catalog: Catalog
  pending: boolean
  designId: string
  onDesignChange: (designId: string) => void
  onSubmit: (designId: string, technologyId: string) => void
}

export function ExperimentForm({ catalog, pending, designId, onDesignChange, onSubmit }: Props) {
  const [technologyId, setTechnologyId] = useState(
    () => catalog.technologies.find((item) => item.available)?.id ?? '',
  )
  const technology = catalog.technologies.find((item) => item.id === technologyId)
  const design = catalog.designs.find((item) => item.id === designId) ?? catalog.designs[0]
  return (
    <section className="panel config-panel" aria-labelledby="config-title">
      <div className="panel-heading">
        <span className="step-number">01</span>
        <div>
          <h2 id="config-title">Configurar evaluación</h2>
          <p>Elige la DPU, su formato y la biblioteca.</p>
        </div>
      </div>
      <label className="field-label" htmlFor="design">
        Diseño y formato numérico
      </label>
      <select
        id="design"
        value={design.id}
        disabled={pending}
        onChange={(event) => onDesignChange(event.target.value)}
      >
        {catalog.designs.map((item) => (
          <option key={item.id} value={item.id}>
            {item.label} · registrada
          </option>
        ))}
      </select>
      <div className="design-details">
        <span>
          Operandos <b>{design.operand_bits} bits</b>
        </span>
        <span>
          Resultado <b>{design.result_bits} bits</b>
        </span>
        <span>
          Registros RTL <b>{design.declared_register_bits} bits</b>
        </span>
      </div>
      <p className="form-footnote">{design.numeric_notes}</p>
      <fieldset className="technology-list">
        <legend>Tecnología de celdas</legend>
        {catalog.technologies.map((item) => (
          <label
            key={item.id}
            className={`technology ${technologyId === item.id ? 'selected' : ''} ${!item.available ? 'unavailable' : ''}`}
          >
            <input
              type="radio"
              name="technology"
              value={item.id}
              checked={technologyId === item.id}
              disabled={!item.available || pending}
              onChange={() => setTechnologyId(item.id)}
            />
            <span className="radio-icon">
              {item.available ? (
                <Check size={14} aria-hidden="true" />
              ) : (
                <CircleDashed size={16} aria-hidden="true" />
              )}
            </span>
            <span className="technology-copy">
              <strong>{item.label}</strong>
              <small>
                {item.available
                  ? `${item.corner} · ${item.voltage_v} V · ${item.temperature_c} °C`
                  : 'Pendiente: falta archivo .lib'}
              </small>
            </span>
            <span className="node-tag">{item.node_nm} nm</span>
          </label>
        ))}
      </fieldset>
      <div className="scope-note">
        <strong>Área de celdas estándar</strong>
        <p>Incluye lógica y registros. Excluye conexiones, routing y área del chip completo.</p>
      </div>
      <button
        className="button primary"
        disabled={pending || !technology?.available}
        onClick={() => onSubmit(design.id, technologyId)}
      >
        {pending ? 'Creando evaluación…' : 'Calcular área'}
        <ArrowRight size={17} aria-hidden="true" />
      </button>
      <p className="form-footnote">Ejecuta GHDL y Yosys sobre el RTL existente.</p>
    </section>
  )
}
