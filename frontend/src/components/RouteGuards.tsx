import type { PropsWithChildren } from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { dashboardPath } from '../lib/routes'
import type { UserRole } from '../types/auth'

export function AuthLoading() {
  return <main className="loading-screen"><span className="loading-mark" /><p>Preparing your workspace…</p></main>
}

export function RequireAuth({ roles }: { roles?: UserRole[] }) {
  const { user, loading } = useAuth()
  const location = useLocation()
  if (loading) return <AuthLoading />
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />
  if (roles && !roles.includes(user.role)) return <Navigate to={dashboardPath(user.role)} replace />
  return <Outlet />
}

export function GuestOnly({ children }: PropsWithChildren) {
  const { user, loading } = useAuth()
  if (loading) return <AuthLoading />
  return user ? <Navigate to={dashboardPath(user.role)} replace /> : children
}
