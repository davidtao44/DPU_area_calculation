import { z } from 'zod'
import { catalogSchema, experimentSchema } from './contracts'

const base = import.meta.env.VITE_API_BASE_URL ?? ''

export function apiUrl(path: string): string {
  return `${base}${path}`
}

async function request<T>(path: string, schema: z.ZodType<T>, options?: RequestInit): Promise<T> {
  const response = await fetch(apiUrl(path), options)
  const data: unknown = await response.json()
  if (!response.ok) {
    const error = z.object({ detail: z.string() }).safeParse(data)
    throw new Error(error.success ? error.data.detail : `Error HTTP ${response.status}`)
  }
  return schema.parse(data)
}

export const api = {
  catalog: (signal?: AbortSignal) => request('/api/v1/catalog', catalogSchema, { signal }),
  experiments: (signal?: AbortSignal) =>
    request('/api/v1/experiments', z.array(experimentSchema), { signal }),
  create: (designId: string, technologyId: string) =>
    request('/api/v1/experiments', experimentSchema, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ design_id: designId, technology_id: technologyId }),
    }),
  logs: (id: string, signal?: AbortSignal) =>
    request(
      `/api/v1/experiments/${id}/logs`,
      z.object({ content: z.string(), truncated: z.boolean() }),
      { signal },
    ),
}
