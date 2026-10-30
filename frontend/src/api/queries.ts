import { apiRequest } from './http'
import type { Category, CreateQueryRequest, QueryDetail, QueryResponse } from '../types/query'

export const queryApi = {
  listCategories: (token: string) => apiRequest<Category[]>('/api/categories', { token }),
  listMine: (token: string) => apiRequest<QueryResponse[]>('/api/queries', { token }),
  getMine: (token: string, queryId: string) => apiRequest<QueryDetail>(`/api/queries/${encodeURIComponent(queryId)}`, { token }),
  create: (token: string, payload: CreateQueryRequest) => apiRequest<QueryResponse>('/api/queries', {
    token,
    method: 'POST',
    body: JSON.stringify(payload),
  }),
}
