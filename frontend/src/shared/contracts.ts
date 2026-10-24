import { z } from 'zod'

export const technologySchema = z.object({
  id: z.string(),
  label: z.string(),
  node_nm: z.number(),
  corner: z.string(),
  voltage_v: z.number(),
  temperature_c: z.number(),
  available: z.boolean(),
  reason: z.string().nullable(),
  area_unit: z.string(),
})

export const catalogSchema = z.object({
  designs: z
    .array(
      z.object({
        id: z.string(),
        label: z.string(),
        numeric_format: z.string(),
        top: z.string(),
        declared_register_bits: z.number(),
        operand_bits: z.number().int().positive(),
        result_bits: z.number().int().positive(),
        numeric_notes: z.string(),
      }),
    )
    .min(1),
  technologies: z.array(technologySchema),
})

export const reportSchema = z.object({
  total_area: z.number().nonnegative(),
  combinational_area: z.number().nonnegative(),
  sequential_area: z.number().nonnegative(),
  macro_area: z.number().nonnegative(),
  flip_flop_area: z.number(),
  latch_area: z.number(),
  total_cells: z.number(),
  cell_counts: z.object({
    combinational: z.number(),
    flip_flop: z.number(),
    latch: z.number(),
    macro: z.number(),
  }),
  cells: z.array(
    z.object({
      name: z.string(),
      category: z.string(),
      count: z.number(),
      unit_area: z.number(),
      total_area: z.number(),
    }),
  ),
  area_unit: z.string(),
  area_unit_basis: z.string(),
  top: z.string(),
  numeric_format: z.string(),
  declared_register_bits: z.number().int().positive().optional(),
  technology_label: z.string(),
  technology_id: z.string(),
  node_nm: z.number(),
  corner: z.string(),
  voltage_v: z.number(),
  temperature_c: z.number(),
  duration_seconds: z.number(),
  validation: z.object({
    rtl: z.string(),
    mapped: z.string(),
    vectors: z.number(),
    seed: z.number(),
    formal_equivalence: z.string(),
    timing_analysis: z.string(),
    reference: z.enum(['signed_dot_modulo', 'rtl_bit_exact']).optional(),
    numerical_accuracy: z.string().optional(),
  }),
  manifest: z.object({
    liberty_sha256: z.string(),
    tool_versions: z.record(z.string()),
    source_sha256: z.record(z.string()),
    mapping_policy: z.string(),
  }),
})

export const experimentSchema = z.object({
  id: z.string(),
  design_id: z.string(),
  technology_id: z.string(),
  status: z.enum(['queued', 'running', 'succeeded', 'failed', 'interrupted']),
  stage: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
  error: z.string().nullable(),
  report: reportSchema.nullable(),
})

export type Catalog = z.infer<typeof catalogSchema>
export type Technology = z.infer<typeof technologySchema>
export type Experiment = z.infer<typeof experimentSchema>
export type AreaReport = z.infer<typeof reportSchema>
