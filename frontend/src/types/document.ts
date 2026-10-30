export interface DocumentRecord {
  id: string
  title: string
  filename: string
  file_path: string
  uploaded_by: string
  created_at: string
}

export interface DeleteDocumentResponse {
  message: string
}
