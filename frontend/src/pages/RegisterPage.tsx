import { ArrowRight, Eye, EyeOff, LockKeyhole, Mail, UserRound } from 'lucide-react'
import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { ApiError } from '../api/http'
import { AuthShell } from '../components/AuthShell'
import { useAuth } from '../context/AuthContext'
import { dashboardPath } from '../lib/routes'

export function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    if (password.length < 10) { setError('Use a password with at least 10 characters.'); return }
    setSubmitting(true)
    try {
      const user = await register({ email: email.trim(), full_name: fullName.trim(), password })
      setPassword('')
      navigate(dashboardPath(user.role), { replace: true })
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : 'We could not create your account. Please try again.')
      setPassword('')
    } finally {
      setSubmitting(false)
    }
  }

  return <AuthShell mode="register">
    <div className="form-heading"><span className="section-kicker">A PLACE TO BEGIN</span><h1>Make room for<br /><em>better answers.</em></h1><p>Create your student account in just a moment.</p></div>
    <form className="auth-form register-form" onSubmit={handleSubmit}>
      {error && <div className="form-alert" role="alert">{error}</div>}
      <label className="field-label" htmlFor="fullName">Full name</label>
      <div className="input-wrap"><UserRound size={17} aria-hidden="true" /><input id="fullName" type="text" autoComplete="name" placeholder="Your name" value={fullName} onChange={(event) => setFullName(event.target.value)} minLength={1} maxLength={200} required /></div>
      <label className="field-label" htmlFor="email">Email address</label>
      <div className="input-wrap"><Mail size={17} aria-hidden="true" /><input id="email" type="email" autoComplete="email" placeholder="you@university.edu" value={email} onChange={(event) => setEmail(event.target.value)} required /></div>
      <label className="field-label" htmlFor="password">Password <span className="label-hint">At least 10 characters</span></label>
      <div className="input-wrap"><LockKeyhole size={17} aria-hidden="true" /><input id="password" type={showPassword ? 'text' : 'password'} autoComplete="new-password" placeholder="Create a password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={10} required /><button className="visibility-toggle" type="button" onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? 'Hide password' : 'Show password'}>{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button></div>
      <button className="primary-button" type="submit" disabled={submitting}>{submitting ? <><span className="button-spinner" /> Creating account…</> : <>Create student account <ArrowRight size={17} /></>}</button>
      <p className="terms-note">By continuing, you agree to use your account for academic support.</p>
    </form>
  </AuthShell>
}
