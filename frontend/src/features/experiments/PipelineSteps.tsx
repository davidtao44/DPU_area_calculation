import { Check, LoaderCircle, Minus } from 'lucide-react'
import type { Experiment } from '../../shared/contracts'

const steps = [
  { label: 'VHDL', stages: ['preparing', 'analyzing'] },
  { label: 'Validación RTL', stages: ['validating_rtl'] },
  { label: 'Verilog', stages: ['converting'] },
  { label: 'Mapeo ASIC', stages: ['mapping', 'checking'] },
  { label: 'Validación netlist', stages: ['validating_mapped'] },
  { label: 'Reporte', stages: ['reporting', 'completed'] },
]

export function PipelineSteps({ experiment }: { experiment?: Experiment }) {
  const current = steps.findIndex((step) => step.stages.includes(experiment?.stage ?? ''))
  const succeeded = experiment?.status === 'succeeded'
  const running = experiment?.status === 'running'
  return (
    <ol className="pipeline" aria-label="Etapas del pipeline">
      {steps.map((step, index) => {
        const done = succeeded || (current >= 0 && index < current)
        const active = running && index === current
        return (
          <li
            key={step.label}
            className={done ? 'done' : active ? 'active' : ''}
            aria-current={active ? 'step' : undefined}
          >
            <span className="pipeline-icon">
              {done ? (
                <Check size={14} aria-hidden="true" />
              ) : active ? (
                <LoaderCircle size={15} className="spin" aria-hidden="true" />
              ) : (
                <Minus size={13} aria-hidden="true" />
              )}
            </span>
            <span>{step.label}</span>
          </li>
        )
      })}
    </ol>
  )
}
