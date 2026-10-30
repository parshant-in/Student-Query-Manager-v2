import { apiRequest } from './http'
import type { LoginRequest, RegisterRequest, TokenResponse, User } from '../types/auth'

export const authApi = {
  login: (payload: LoginRequest) => apiRequest<TokenResponse>('/api/auth/login', {
    method: 'POST', body: JSON.stringify(payload),
  }),
  register: (payload: RegisterRequest) => apiRequest<TokenResponse>('/api/auth/register', {
    method: 'POST', body: JSON.stringify(payload),
  }),
  me: (token: string) => apiRequest<User>('/api/auth/me', { token }),
}
