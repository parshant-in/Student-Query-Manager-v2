import type { UserRole } from '../types/auth'

export function dashboardPath(role: UserRole) {
  return `/${role}/dashboard`
}
