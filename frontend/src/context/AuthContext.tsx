import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { PropsWithChildren } from 'react'
import { authApi } from '../api/auth'
import { ApiError } from '../api/http'
import type { LoginRequest, RegisterRequest, User } from '../types/auth'

const TOKEN_KEY = 'sqm_access_token'

interface AuthContextValue {
  user: User | null
  token: string | null
  loading: boolean
  authError: string | null
  login: (payload: LoginRequest) => Promise<User>
  register: (payload: RegisterRequest) => Promise<User>
  logout: () => void
  clearAuthError: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: PropsWithChildren) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [authError, setAuthError] = useState<string | null>(null)

  const clearSession = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    setToken(null)
    setUser(null)
  }, [])

  useEffect(() => {
    let active = true
    if (!token) {
      setLoading(false)
      return () => { active = false }
    }
    setLoading(true)
    authApi.me(token).then((currentUser) => {
      if (active) setUser(currentUser)
    }).catch((error: unknown) => {
      if (!active) return
      clearSession()
      if (error instanceof ApiError && error.status !== 401) {
        setAuthError(`Could not restore your session: ${error.message}`)
      } else if (!(error instanceof ApiError)) {
        setAuthError('Could not verify your saved session. Check your connection and sign in again.')
      }
    }).finally(() => {
      if (active) setLoading(false)
    })
    return () => { active = false }
  }, [token, clearSession])

  const login = useCallback(async (payload: LoginRequest) => {
    setAuthError(null)
    const result = await authApi.login(payload)
    localStorage.setItem(TOKEN_KEY, result.access_token)
    setToken(result.access_token)
    setUser(result.user)
    return result.user
  }, [])

  const register = useCallback(async (payload: RegisterRequest) => {
    setAuthError(null)
    const result = await authApi.register(payload)
    localStorage.setItem(TOKEN_KEY, result.access_token)
    setToken(result.access_token)
    setUser(result.user)
    return result.user
  }, [])

  const value = useMemo(() => ({
    user, token, loading, authError, login, register, logout: clearSession,
    clearAuthError: () => setAuthError(null),
  }), [user, token, loading, authError, login, register, clearSession])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const value = useContext(AuthContext)
  if (!value) throw new Error('useAuth must be used inside AuthProvider')
  return value
}
