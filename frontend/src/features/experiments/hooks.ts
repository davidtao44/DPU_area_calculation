import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../../shared/api'

export function useCatalog() {
  return useQuery({
    queryKey: ['catalog'],
    queryFn: ({ signal }) => api.catalog(signal),
    staleTime: 60_000,
  })
}

export function useExperiments() {
  return useQuery({
    queryKey: ['experiments'],
    queryFn: ({ signal }) => api.experiments(signal),
    refetchInterval: (query) =>
      query.state.data?.some((item) => ['queued', 'running'].includes(item.status)) ? 1500 : 5000,
  })
}

export function useCreateExperiment() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: ({ designId, technologyId }: { designId: string; technologyId: string }) =>
      api.create(designId, technologyId),
    onSuccess: () => client.invalidateQueries({ queryKey: ['experiments'] }),
  })
}
