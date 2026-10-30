import { ArrowRight, Eye, EyeOff, LockKeyhole, Mail } from 'lucide-react'
import { useState, type FormEvent } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { ApiError } from '../api/http'
import { AuthShell } from '../components/AuthShell'
import { useAuth } from '../context/AuthContext'
import { dashboardPath } from '../lib/routes'

export function LoginPage() {
  const { login, authError, clearAuthError } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    clearAuthError()
    setSubmitting(true)
    try {
      const user = await login({ email: email.trim(), password })
      const returnTo = (location.state as { from?: string } | null)?.from
      navigate(returnTo?.startsWith(`/${user.role}/`) ? returnTo : dashboardPath(user.role), { replace: true })
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : 'We could not sign you in. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return <AuthShell mode="login">
    <div className="form-heading"><span className="section-kicker">WELCOME BACK</span><h1>Your next step<br /><em>starts here.</em></h1><p>Sign in to continue your academic journey.</p></div>
    <form className="auth-form" onSubmit={handleSubmit}>
      {(error || authError) && <div className="form-alert" role="alert">{error || authError}</div>}
      <label className="field-label" htmlFor="email">Email address</label>
      <div className="input-wrap"><Mail size={17} aria-hidden="true" /><input id="email" type="email" autoComplete="email" placeholder="you@university.edu" value={email} onChange={(event) => setEmail(event.target.value)} required /></div>
      <div className="label-row"><label className="field-label" htmlFor="password">Password</label></div>
      <div className="input-wrap"><LockKeyhole size={17} aria-hidden="true" /><input id="password" type={showPassword ? 'text' : 'password'} autoComplete="current-password" placeholder="Enter your password" value={password} onChange={(event) => setPassword(event.target.value)} required /><button className="visibility-toggle" type="button" onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? 'Hide password' : 'Show password'}>{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button></div>
      <button className="primary-button" type="submit" disabled={submitting}>{submitting ? <><span className="button-spinner" /> Signing in…</> : <>Sign in <ArrowRight size={17} /></>}</button>
    </form>
  </AuthShell>
}
