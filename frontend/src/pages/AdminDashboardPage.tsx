import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Database, Eye, EyeOff, KeyRound, LogOut, UserPlus, Users, X } from 'lucide-react'
import { adminApi, type AdminFacultyAccount, type AdminUserAccount } from '../api/admin'
import { ApiError } from '../api/http'
import { queryApi } from '../api/queries'
import { useAuth } from '../context/AuthContext'
import type { Category } from '../types/query'

export function AdminDashboardPage() {
  const { user, token, logout } = useAuth()
  const [faculty, setFaculty] = useState<AdminFacultyAccount[]>([])
  const [students, setStudents] = useState<AdminUserAccount[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [busyId, setBusyId] = useState('')
  const [formBusy, setFormBusy] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [formError, setFormError] = useState('')
  const [form, setForm] = useState({ email: '', full_name: '', password: '', department_id: '' })
  const [resetTarget, setResetTarget] = useState<AdminUserAccount | null>(null)
  const [resetPassword, setResetPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showResetPassword, setShowResetPassword] = useState(false)
  const [resetBusy, setResetBusy] = useState(false)
  const [resetError, setResetError] = useState('')

  const load = useCallback(async () => {
    if (!token) return
    setLoading(true); setError('')
    try {
      const [accounts, studentAccounts, departments] = await Promise.all([adminApi.listFaculty(token), adminApi.listStudents(token), queryApi.listCategories(token)])
      setFaculty(accounts); setStudents(studentAccounts); setCategories(departments)
      setForm((current) => ({ ...current, department_id: current.department_id || departments[0]?.id || '' }))
    } catch (reason) { setError(reason instanceof ApiError ? reason.message : 'Could not load accounts.') }
    finally { setLoading(false) }
  }, [token])
  useEffect(() => { void load() }, [load])

  async function createFaculty(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setFormError(''); setFeedback('')
    if (!token) return
    setFormBusy(true)
    try {
      await adminApi.createFaculty(token, form)
      setForm({ email: '', full_name: '', password: '', department_id: form.department_id })
      setFeedback('Faculty account created and department assigned.')
      await load()
    } catch (reason) { setFormError(reason instanceof ApiError ? reason.message : 'Could not create faculty account.') }
    finally { setFormBusy(false) }
  }

  async function toggleFaculty(account: AdminFacultyAccount) {
    if (!token) return
    setBusyId(account.id); setError('')
    try {
      const updated = await adminApi.setFacultyStatus(token, account.id, !account.is_active)
      setFaculty((current) => current.map((item) => item.id === updated.id ? updated : item))
    } catch (reason) { setError(reason instanceof ApiError ? reason.message : 'Could not update account status.') }
    finally { setBusyId('') }
  }

  async function changeDepartment(account: AdminFacultyAccount, departmentId: string) {
    if (!token || !departmentId || departmentId === account.department_id) return
    setBusyId(account.id); setError('')
    try {
      const updated = await adminApi.setFacultyDepartment(token, account.id, departmentId)
      setFaculty((current) => current.map((item) => item.id === updated.id ? updated : item))
    } catch (reason) { setError(reason instanceof ApiError ? reason.message : 'Could not update department.') }
    finally { setBusyId('') }
  }

  function openReset(account: AdminUserAccount) {
    setResetTarget(account); setResetPassword(''); setConfirmPassword(''); setShowResetPassword(false); setResetError('')
  }
  function closeReset() { if (!resetBusy) setResetTarget(null) }
  async function submitReset(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setResetError('')
    if (!token || !resetTarget) return
    if (resetPassword !== confirmPassword) { setResetError('Passwords do not match.'); return }
    setResetBusy(true)
    try {
      await adminApi.resetPassword(token, resetTarget.id, resetPassword)
      setFeedback(`Password reset for ${resetTarget.full_name}. Existing sessions were signed out.`)
      setResetTarget(null); await load()
    } catch (reason) { setResetError(reason instanceof ApiError ? reason.message : 'Could not reset the password.') }
    finally { setResetBusy(false) }
  }

  return <div className="dashboard-page">
    <header className="dashboard-header"><Link className="dashboard-brand" to="/admin/dashboard"><span className="brand-mark">SQ</span><span>Student Query <b>Manager</b></span></Link><div className="dashboard-account"><span className="account-avatar">{user?.full_name.slice(0, 1).toUpperCase()}</span><span className="account-name">{user?.full_name}</span><button className="logout-button" type="button" onClick={logout}><LogOut size={16} />Sign out</button></div></header>
    <main className="dashboard-main admin-management-main"><div className="dashboard-kicker"><span />ADMIN WORKSPACE</div><h1>Account <em>management.</em></h1><p className="dashboard-intro">Create faculty accounts, assign departments, manage access, and reset student or faculty passwords.</p>
      <section className="welcome-card admin-create-card"><div className="welcome-top"><div><span className="section-kicker">NEW ACCOUNT</span><h2><UserPlus size={18} /> Create faculty account</h2></div></div><form className="admin-faculty-form" onSubmit={createFaculty}><label>Email<input type="email" required value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} autoComplete="off" /></label><label>Full name<input required maxLength={200} value={form.full_name} onChange={(event) => setForm({ ...form, full_name: event.target.value })} /></label><label>Temporary password<input type="password" required minLength={10} value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} autoComplete="new-password" /></label><label>Department<select required value={form.department_id} onChange={(event) => setForm({ ...form, department_id: event.target.value })}><option value="">Choose a department</option>{categories.map((category) => <option value={category.id} key={category.id}>{category.name}</option>)}</select></label>{formError && <p className="inline-feedback feedback-error" role="alert">{formError}</p>}{feedback && <p className="inline-feedback" role="status">{feedback}</p>}<button className="olive-action" type="submit" disabled={formBusy || categories.length === 0}>{formBusy ? 'Creating…' : 'Create faculty account'}</button></form></section>
      <section className="welcome-card admin-faculty-list-card"><div className="welcome-top"><div><span className="section-kicker"><Users size={14} /> ACCOUNTS</span><h2>Faculty accounts {loading ? '' : `(${faculty.length})`}</h2></div><Link className="admin-kb-link" to="/admin/knowledge-base"><Database size={16} /><span><strong>Knowledge base</strong><small>Manage supporting documents</small></span><ArrowRight size={15} /></Link></div>{error && <p className="inline-feedback feedback-error" role="alert">{error} <button className="text-action" type="button" onClick={() => void load()}>Retry</button></p>}{loading ? <p>Loading faculty accounts…</p> : faculty.length === 0 ? <p>No faculty accounts yet.</p> : <div className="admin-faculty-list">{faculty.map((account) => <article key={account.id} className="admin-faculty-row"><div className="admin-faculty-identity"><strong>{account.full_name}</strong><span>{account.email}</span><small>{account.is_active ? 'Enabled' : 'Disabled'}</small></div><label>Department<select value={account.department_id ?? ''} disabled={busyId === account.id} onChange={(event) => void changeDepartment(account, event.target.value)}><option value="" disabled>Unassigned</option>{categories.map((category) => <option value={category.id} key={category.id}>{category.name}</option>)}</select></label><div className="admin-account-actions"><button className="olive-action" type="button" onClick={() => openReset(account)}><KeyRound size={14} />Reset password</button><button className="olive-action" type="button" disabled={busyId === account.id} onClick={() => void toggleFaculty(account)}>{busyId === account.id ? 'Saving…' : account.is_active ? 'Disable' : 'Enable'}</button></div></article>)}</div>}</section>
      <section className="welcome-card admin-faculty-list-card"><div className="welcome-top"><div><span className="section-kicker"><Users size={14} /> ACCOUNTS</span><h2>Student accounts {loading ? '' : `(${students.length})`}</h2></div></div>{loading ? <p>Loading student accounts…</p> : students.length === 0 ? <p>No student accounts yet.</p> : <div className="admin-faculty-list">{students.map((account) => <article key={account.id} className="admin-student-row"><div className="admin-faculty-identity"><strong>{account.full_name}</strong><span>{account.email}</span><small>{account.is_active ? 'Enabled' : 'Disabled'}</small></div><button className="olive-action" type="button" onClick={() => openReset(account)}><KeyRound size={14} />Reset password</button></article>)}</div>}</section>
    </main>
    {resetTarget && <div className="admin-modal-backdrop" role="presentation" onMouseDown={closeReset}><section className="admin-password-modal" role="dialog" aria-modal="true" aria-labelledby="reset-password-title" onMouseDown={(event) => event.stopPropagation()}><button className="admin-modal-close" type="button" onClick={closeReset} disabled={resetBusy} aria-label="Close password reset dialog"><X size={18} /></button><span className="section-kicker">RESET PASSWORD</span><h2 id="reset-password-title">Reset account password</h2><dl><div><dt>Name</dt><dd>{resetTarget.full_name}</dd></div><div><dt>Email</dt><dd>{resetTarget.email}</dd></div><div><dt>Role</dt><dd>{resetTarget.role}</dd></div></dl><form className="admin-reset-form" onSubmit={submitReset}><label>New password<span className="admin-password-field"><input type={showResetPassword ? 'text' : 'password'} minLength={10} required value={resetPassword} onChange={(event) => setResetPassword(event.target.value)} autoComplete="new-password" /><button type="button" onClick={() => setShowResetPassword((visible) => !visible)} aria-label={showResetPassword ? 'Hide password' : 'Show password'}>{showResetPassword ? <EyeOff size={16} /> : <Eye size={16} />}</button></span><small>At least 10 characters.</small></label><label>Confirm password<span className="admin-password-field"><input type={showResetPassword ? 'text' : 'password'} minLength={10} required value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} autoComplete="new-password" /><button type="button" onClick={() => setShowResetPassword((visible) => !visible)} aria-label={showResetPassword ? 'Hide password' : 'Show password'}>{showResetPassword ? <EyeOff size={16} /> : <Eye size={16} />}</button></span></label>{resetError && <p className="inline-feedback feedback-error" role="alert">{resetError}</p>}<div className="admin-modal-actions"><button className="text-action" type="button" onClick={closeReset} disabled={resetBusy}>Cancel</button><button className="olive-action" type="submit" disabled={resetBusy}>{resetBusy ? 'Resetting…' : 'Reset password'}</button></div></form></section></div>}
  </div>
}
