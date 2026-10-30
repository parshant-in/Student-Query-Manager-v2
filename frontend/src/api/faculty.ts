import { apiRequest } from './http'
import type { FacultyDepartment, FacultyResponse, FacultyResponseRequest, QueryDetail, QueryResponse, QueryStatusUpdateRequest } from '../types/query'

const facultyQueriesPath = '/api/faculty/queries'

export const facultyApi = {
  getDepartment: (token: string) => apiRequest<FacultyDepartment>('/api/faculty/department', { token }),
  listAssigned: (token: string) => apiRequest<QueryResponse[]>(facultyQueriesPath, { token }),
  getAssigned: (token: string, queryId: string) => apiRequest<QueryDetail>(`${facultyQueriesPath}/${encodeURIComponent(queryId)}`, { token }),
  claim: (token: string, queryId: string) => apiRequest<QueryResponse>(`${facultyQueriesPath}/${encodeURIComponent(queryId)}/claim`, {
    token,
    method: 'POST',
  }),
  respond: (token: string, queryId: string, payload: FacultyResponseRequest) => apiRequest<FacultyResponse>(`${facultyQueriesPath}/${encodeURIComponent(queryId)}/response`, {
    token,
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  updateStatus: (token: string, queryId: string, payload: QueryStatusUpdateRequest) => apiRequest<QueryResponse>(`${facultyQueriesPath}/${encodeURIComponent(queryId)}/status`, {
    token,
    method: 'PATCH',
    body: JSON.stringify(payload),
  }),
}
