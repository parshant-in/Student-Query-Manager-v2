export type QueryStatus = 'pending' | 'solved' | 'unsolved'

export interface Category {
  id: string
  name: string
  description: string
}

export interface QueryResponse {
  id: string
  student_id: string
  category_id: string
  faculty_id: string | null
  title: string
  description: string
  status: QueryStatus
  created_at: string
  updated_at: string
}

export interface FacultyResponse {
  id: string
  query_id: string
  faculty_id: string
  message: string
  created_at: string
}

export interface QueryDetail extends QueryResponse {
  responses: FacultyResponse[]
}

export interface CreateQueryRequest {
  category_id: string
  title: string
  description: string
}

export interface FacultyResponseRequest {
  message: string
}

export interface QueryStatusUpdateRequest {
  status: QueryStatus
}

export interface FacultyDepartment {
  department_id: string | null
}
