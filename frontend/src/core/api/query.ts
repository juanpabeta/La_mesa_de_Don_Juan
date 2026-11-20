import { useQuery } from '@tanstack/react-query';
export function useResourceQuery<T>(key: string, load: () => Promise<T>, _legacyInitialData?: T) {
  return useQuery({
    queryKey: [key],
    queryFn: load,
    staleTime: 15_000,
    retry: 1,
  });
}
