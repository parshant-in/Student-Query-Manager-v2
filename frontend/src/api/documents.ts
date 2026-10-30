import { apiRequest } from './http'
import type { DeleteDocumentResponse, DocumentRecord } from '../types/document'

export const documentApi = {
  list: (token: string) => apiRequest<DocumentRecord[]>('/api/documents', { token }),
  get: (token: string, documentId: string) => apiRequest<DocumentRecord>(`/api/documents/${encodeURIComponent(documentId)}`, { token }),
  upload: (token: string, file: File, title: string) => {
    const form = new FormData()
    form.append('file', file)
    const params = new URLSearchParams()
    if (title.trim()) params.set('title', title.trim())
    const query = params.size ? `?${params.toString()}` : ''
    return apiRequest<DocumentRecord>(`/api/documents${query}`, {
      token,
      method: 'POST',
      body: form,
    })
  },
  delete: (token: string, documentId: string) => apiRequest<DeleteDocumentResponse>(`/api/documents/${encodeURIComponent(documentId)}`, {
    token,
    method: 'DELETE',
  }),
}
