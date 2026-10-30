import { apiRequest } from './http'

export interface AdminUserAccount {
  id: string
  email: string
  full_name: string
  role: 'student' | 'faculty'
  department_id: string | null
  is_active: boolean
  created_at: string
}

export type AdminFacultyAccount = AdminUserAccount

export interface CreateFacultyPayload {
  email: string
  full_name: string
  password: string
  department_id: string
}

export const adminApi = {
  listFaculty: (token: string) => apiRequest<AdminFacultyAccount[]>('/api/admin/faculty', { token }),
  listStudents: (token: string) => apiRequest<AdminUserAccount[]>('/api/admin/students', { token }),
  createFaculty: (token: string, payload: CreateFacultyPayload) => apiRequest<AdminFacultyAccount>('/api/admin/faculty', {
    token, method: 'POST', body: JSON.stringify(payload),
  }),
  setFacultyStatus: (token: string, facultyId: string, isActive: boolean) => apiRequest<AdminFacultyAccount>(`/api/admin/faculty/${encodeURIComponent(facultyId)}/status`, {
    token, method: 'PATCH', body: JSON.stringify({ is_active: isActive }),
  }),
  setFacultyDepartment: (token: string, facultyId: string, departmentId: string) => apiRequest<AdminFacultyAccount>(`/api/admin/faculty/${encodeURIComponent(facultyId)}/department`, {
    token, method: 'PATCH', body: JSON.stringify({ department_id: departmentId }),
  }),
  resetPassword: (token: string, userId: string, newPassword: string) => apiRequest<AdminUserAccount>(`/api/admin/users/${encodeURIComponent(userId)}/reset-password`, {
    token, method: 'POST', body: JSON.stringify({ new_password: newPassword }),
  }),
}
