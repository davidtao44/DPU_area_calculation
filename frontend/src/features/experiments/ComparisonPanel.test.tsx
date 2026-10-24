import { fireEvent, render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import actualReport from '../../../../docs/validation/nangate45-report.json'
import type { Experiment, Technology } from '../../shared/contracts'
import { ComparisonPanel } from './ComparisonPanel'

const technologies: Technology[] = [
  {
    id: 'nangate45',
    label: 'Nangate45',
    node_nm: 45,
    corner: 'typical',
    voltage_v: 1.1,
    temperature_c: 25,
    available: true,
    reason: null,
    area_unit: 'um2',
  },
  {
    id: 'ihp130',
    label: 'IHP',
    node_nm: 130,
    corner: 'typical',
    voltage_v: 1.2,
    temperature_c: 25,
    available: true,
    reason: null,
    area_unit: 'um2',
  },
]

function example(id: string, designId: string, technologyId: string, created: string): Experiment {
  return {
    id,
    design_id: designId,
    technology_id: technologyId,
    created_at: created,
    updated_at: created,
    status: 'succeeded',
    stage: 'completed',
    error: null,
    report: {
      ...actualReport,
      numeric_format: designId.toUpperCase(),
      technology_id: technologyId,
      technology_label: technologyId,
    },
  }
}

const experiments = [
  example('old', 'int8_16', 'nangate45', '2026-10-01'),
  example('fp16', 'fp16', 'nangate45', '2026-10-18'),
  example('latest', 'int8_16', 'nangate45', '2026-10-18'),
  example('ihp', 'fp16', 'ihp130', '2026-10-18'),
]

test('technology comparison filters by design and keeps only the latest success', () => {
  const { rerender } = render(
    <ComparisonPanel experiments={experiments} designId="int8_16" technologies={technologies} />,
  )
  expect(screen.getAllByRole('img')).toHaveLength(1)
  expect(screen.getByRole('img', { name: /^INT8_16, nangate45/ })).toBeInTheDocument()
  expect(screen.queryByRole('img', { name: /^FP16/ })).not.toBeInTheDocument()
  rerender(
    <ComparisonPanel experiments={experiments} designId="fp16" technologies={technologies} />,
  )
  expect(screen.getAllByRole('img')).toHaveLength(2)
})

test('format comparison keeps one technology and supports switching its library', () => {
  render(
    <ComparisonPanel experiments={experiments} designId="int8_16" technologies={technologies} />,
  )
  fireEvent.change(screen.getByRole('combobox', { name: 'Comparar' }), {
    target: { value: 'format' },
  })
  expect(screen.getAllByRole('img')).toHaveLength(2)
  expect(screen.queryByRole('img', { name: /, ihp130/ })).not.toBeInTheDocument()
  fireEvent.change(screen.getByRole('combobox', { name: 'Biblioteca de comparación' }), {
    target: { value: 'ihp130' },
  })
  expect(screen.getAllByRole('img')).toHaveLength(1)
  expect(screen.getByRole('img', { name: /^FP16, ihp130/ })).toBeInTheDocument()
})
