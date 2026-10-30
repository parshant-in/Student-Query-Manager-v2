import { ArrowRight, Check, CircleHelp, Clock3, Landmark } from 'lucide-react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { ApiError } from '../api/http'
import { facultyApi } from '../api/faculty'
import { queryApi } from '../api/queries'
import { ErrorBlock, LoadingBlock, QueryListItem } from '../components/QueryUI'
import { useAuth } from '../context/AuthContext'
import type { Category, QueryResponse } from '../types/query'

function getErrorMessage(error: unknown) {
  if (error instanceof ApiError) return error.status === 401 ? 'Your session has expired. Please sign in again.' : error.message
  return 'Check your connection and try again.'
}

export function FacultyDashboardPage() {
  const { user, token } = useAuth()
  const [queries, setQueries] = useState<QueryResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [categories, setCategories] = useState<Category[]>([])
  const [departmentId, setDepartmentId] = useState('')
  const [departmentError, setDepartmentError] = useState('')
  const loadQueries = useCallback(async () => {
    if (!token) return
    setLoading(true); setError('')
    try { setQueries(await facultyApi.listAssigned(token)) }
    catch (reason) { setError(getErrorMessage(reason)) }
    finally { setLoading(false) }
  }, [token])
  useEffect(() => { void loadQueries() }, [loadQueries])
  useEffect(() => {
    if (!token) return
    Promise.all([facultyApi.getDepartment(token), queryApi.listCategories(token)]).then(([department, available]) => {
      setDepartmentId(department.department_id ?? '')
      setCategories(available)
    }).catch((reason: unknown) => setDepartmentError(getErrorMessage(reason)))
  }, [token])

  const recentQueries = useMemo(() => [...queries].sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at)).slice(0, 4), [queries])
  const pending = queries.filter((query) => query.status === 'pending').length
  const solved = queries.filter((query) => query.status === 'solved').length
  const unsolved = queries.filter((query) => query.status === 'unsolved').length

  return <div className="student-page">
    <div className="student-welcome-row"><div><div className="student-eyebrow"><span />FACULTY WORKSPACE</div><h1>Good to have you here,<br /><em>{user?.full_name.split(' ')[0] ?? 'Faculty'}.</em></h1><p>Review assigned queries and support students with clear guidance.</p></div><Link to="/faculty/queries" className="olive-action"><CircleHelp size={16} />View assigned queries</Link></div>
    <div className="student-stat-grid faculty-stat-grid" aria-label="Assigned query summary">
      <article className="student-stat-card"><div className="stat-icon stat-icon-olive"><CircleHelp size={17} /></div><span className="stat-label">DEPARTMENT QUEUE</span><strong>{loading || error ? '—' : queries.length}</strong><small>All queries in your department</small></article>
      <article className="student-stat-card"><div className="stat-icon stat-icon-bronze"><Clock3 size={17} /></div><span className="stat-label">PENDING</span><strong>{loading || error ? '—' : pending}</strong><small>Awaiting your response</small></article>
      <article className="student-stat-card"><div className="stat-icon stat-icon-sage"><Check size={17} /></div><span className="stat-label">SOLVED</span><strong>{loading || error ? '—' : solved}</strong><small>Marked as resolved</small></article>
      <article className="student-stat-card"><div className="stat-icon stat-icon-stone"><CircleHelp size={17} /></div><span className="stat-label">UNSOLVED</span><strong>{loading || error ? '—' : unsolved}</strong><small>Still needing attention</small></article>
    </div>
    <section className="student-panel faculty-department-panel"><div className="composer-heading"><span className="form-panel-icon"><Landmark size={17} /></span><div><span className="section-kicker">FACULTY PROFILE</span><h2>Assigned department</h2></div></div><p className="faculty-department-copy">Your department is assigned by an administrator. Queries for this department appear in your queue; claim a query before responding.</p><p className="inline-feedback">{categories.find((category) => category.id === departmentId)?.name ?? (departmentId ? 'Assigned department' : 'No department assigned. Contact an administrator.')}</p>{departmentError && <p className="inline-feedback feedback-error" role="alert">{departmentError}</p>}</section>
    <section className="student-panel faculty-recent-panel"><div className="panel-heading"><div><span className="section-kicker">YOUR DEPARTMENT QUEUE</span><h2>Recent queries</h2></div><Link to="/faculty/queries" className="subtle-link">View all <ArrowRight size={14} /></Link></div>
      {error ? <ErrorBlock message={error} onRetry={() => void loadQueries()} /> : loading ? <LoadingBlock label="Loading department queries…" /> : recentQueries.length === 0 ? <div className="empty-state"><span className="empty-icon"><CircleHelp size={19} /></span><h3>{departmentId ? 'No queries in your queue yet.' : 'Choose your department to see its query queue.'}</h3><p>New student queries for your department will appear here.</p></div> : <div className="query-list">{recentQueries.map((query) => <QueryListItem key={query.id} query={query} to={`/faculty/queries/${query.id}`} metadata={`${categories.find((category) => category.id === query.category_id)?.name ?? 'Department'} · ${query.faculty_id ? 'Claimed' : 'Available to claim'}`} />)}</div>}
    </section>
    <div className="faculty-note"><span>FACULTY ACCESS</span><p>Query access and actions follow the assignments and permissions provided by the backend.</p></div>
  </div>
}
