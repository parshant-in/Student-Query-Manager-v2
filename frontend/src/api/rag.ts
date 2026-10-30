import { apiRequest } from './http'
import type { RagAskRequest, RagAskResponse } from '../types/rag'

export const ragApi = {
  ask: (token: string, payload: RagAskRequest) => apiRequest<RagAskResponse>('/api/rag/ask', {
    token,
    method: 'POST',
    body: JSON.stringify(payload),
  }),
}
