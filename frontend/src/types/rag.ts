export interface RagAskRequest {
  question: string
}

export interface RagSource {
  document_id: string
  title: string
  filename: string
  score: number
}

export interface RagAskResponse {
  answer: string
  sources: RagSource[]
}
