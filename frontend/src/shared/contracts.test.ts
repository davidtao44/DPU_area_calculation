import { expect, test } from 'vitest'
import ihpReport from '../../../docs/validation/ihp130-report.json'
import nangateReport from '../../../docs/validation/nangate15-report.json'
import nangate45Report from '../../../docs/validation/nangate45-report.json'
import { reportSchema } from './contracts'

test.each([ihpReport, nangateReport, nangate45Report])(
  'accepts an actual verified backend report',
  (report) => {
    const parsed = reportSchema.parse(report)
    expect(parsed.validation.rtl).toBe('passed')
    expect(parsed.validation.mapped).toBe('passed')
    expect(parsed.cell_counts.flip_flop).toBe(96)
    expect(parsed.total_area).toBeGreaterThan(0)
  },
)

test('rejects a malformed area response before it reaches the UI', () => {
  expect(reportSchema.safeParse({ ...ihpReport, total_area: -1 }).success).toBe(false)
})

const matrixReports = import.meta.glob(
  '../../../docs/validation/dpu-matrix-20261018/**/report.json',
  { eager: true, import: 'default' },
)

test('covers the ten validated DPU profiles in all three technologies', () => {
  expect(Object.keys(matrixReports)).toHaveLength(30)
})

test.each(Object.entries(matrixReports))('accepts the verified DPU report %s', (_path, report) => {
  const parsed = reportSchema.parse(report)
  expect(parsed.validation.rtl).toBe('passed')
  expect(parsed.validation.mapped).toBe('passed')
  expect(parsed.validation.vectors).toBe(256)
  expect(parsed.cell_counts.flip_flop).toBeGreaterThan(0)
  expect(parsed.declared_register_bits).toBeDefined()
  expect(parsed.cell_counts.flip_flop).toBeLessThanOrEqual(parsed.declared_register_bits!)
  expect(parsed.total_area).toBeCloseTo(parsed.combinational_area + parsed.sequential_area, 5)
})
