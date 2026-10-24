import { fireEvent, render, screen } from '@testing-library/react'
import { expect, test, vi } from 'vitest'
import type { Catalog } from '../../shared/contracts'
import { ExperimentForm } from './ExperimentForm'
import { ReportPanel } from './ReportPanel'

const selectionProps = { designId: 'int8_16', onDesignChange: vi.fn() }

const catalog: Catalog = {
  designs: [
    {
      id: 'int8_16',
      label: 'DPU INT8',
      numeric_format: 'INT8_16',
      top: 'INT8_16_DPU_perf_top',
      declared_register_bits: 96,
      operand_bits: 8,
      result_bits: 16,
      numeric_notes: 'Enteros con signo',
    },
    {
      id: 'fp16',
      label: 'DPU FP16',
      numeric_format: 'FP16',
      top: 'FP16_DPU_perf_top',
      declared_register_bits: 160,
      operand_bits: 16,
      result_bits: 16,
      numeric_notes: 'Cuatro FMA encadenadas',
    },
  ],
  technologies: [
    {
      id: 'ihp130',
      label: 'IHP SG13G2',
      node_nm: 130,
      corner: 'typical',
      voltage_v: 1.2,
      temperature_c: 25,
      available: true,
      reason: null,
      area_unit: 'um2',
    },
    {
      id: 'nangate45',
      label: 'Nangate45',
      node_nm: 45,
      corner: 'typical',
      voltage_v: 1.1,
      temperature_c: 25,
      available: false,
      reason: 'Missing .lib',
      area_unit: 'um2',
    },
  ],
}

test('unavailable technology cannot be selected and submit uses the chosen library', () => {
  const onSubmit = vi.fn()
  render(
    <ExperimentForm {...selectionProps} catalog={catalog} pending={false} onSubmit={onSubmit} />,
  )
  expect(screen.getByRole('radio', { name: /Nangate45/ })).toBeDisabled()
  expect(screen.getByRole('radio', { name: /IHP SG13G2/ })).toBeChecked()
  fireEvent.click(screen.getByRole('button', { name: /Calcular área/ }))
  expect(onSubmit).toHaveBeenCalledWith('int8_16', 'ihp130')
})

test('empty state never presents invented area results', () => {
  render(<ReportPanel />)
  expect(screen.getByText('Tu primera medición empieza aquí')).toBeInTheDocument()
  expect(screen.queryByText('ÁREA TOTAL DE CELDAS')).not.toBeInTheDocument()
})

test('available Nangate45 can be selected and submitted', () => {
  const onSubmit = vi.fn()
  const availableCatalog: Catalog = {
    ...catalog,
    technologies: catalog.technologies.map((item) => ({
      ...item,
      available: true,
      reason: null,
    })),
  }
  render(
    <ExperimentForm
      {...selectionProps}
      catalog={availableCatalog}
      pending={false}
      onSubmit={onSubmit}
    />,
  )
  const technology = screen.getByRole('radio', { name: /Nangate45/ })
  expect(technology).toBeEnabled()
  fireEvent.click(technology)
  expect(technology).toBeChecked()
  fireEvent.click(screen.getByRole('button', { name: /Calcular área/ }))
  expect(onSubmit).toHaveBeenCalledWith('int8_16', 'nangate45')
})

test('pending submit prevents duplicate creation', () => {
  render(<ExperimentForm {...selectionProps} catalog={catalog} pending onSubmit={vi.fn()} />)
  expect(screen.getByRole('button', { name: /Creando evaluación/ })).toBeDisabled()
})

test('changing DPU updates widths and submits the chosen design', () => {
  const onSubmit = vi.fn()
  const onDesignChange = vi.fn()
  const { rerender } = render(
    <ExperimentForm
      catalog={catalog}
      pending={false}
      designId="int8_16"
      onDesignChange={onDesignChange}
      onSubmit={onSubmit}
    />,
  )
  fireEvent.change(screen.getByRole('combobox', { name: /Diseño y formato/ }), {
    target: { value: 'fp16' },
  })
  expect(onDesignChange).toHaveBeenCalledWith('fp16')
  rerender(
    <ExperimentForm
      catalog={catalog}
      pending={false}
      designId="fp16"
      onDesignChange={onDesignChange}
      onSubmit={onSubmit}
    />,
  )
  expect(screen.getByText('160 bits')).toBeInTheDocument()
  expect(screen.getByText('Cuatro FMA encadenadas')).toBeInTheDocument()
  fireEvent.click(screen.getByRole('button', { name: /Calcular área/ }))
  expect(onSubmit).toHaveBeenCalledWith('fp16', 'ihp130')
})
