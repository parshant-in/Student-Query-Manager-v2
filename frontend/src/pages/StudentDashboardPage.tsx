import { ArrowRight, Check, CircleHelp, Clock3, Plus, Sparkles } from 'lucide-react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { queryApi } from '../api/queries'
import { ApiError } from '../api/http'
import { ErrorBlock, LoadingBlock, QueryListItem } from '../components/QueryUI'
import { useAuth } from '../context/AuthContext'
import type { QueryResponse } from '../types/query'

function getErrorMessage(error: unknown) {
  if (error instanceof ApiError) return error.status === 401 ? 'Your session has expired. Please sign in again.' : error.message
  return 'Check your connection and try again.'
}

export function StudentDashboardPage() {
  const { user, token } = useAuth()
  const [queries, setQueries] = useState<QueryResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const loadQueries = useCallback(async () => {
    if (!token) return
    setLoading(true)
    setError('')
    try { setQueries(await queryApi.listMine(token)) }
    catch (reason) { setError(getErrorMessage(reason)) }
    finally { setLoading(false) }
  }, [token])
  useEffect(() => { void loadQueries() }, [loadQueries])

  const recentQueries = useMemo(() => [...queries].sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at)).slice(0, 3), [queries])
  const pending = queries.filter((query) => query.status === 'pending').length
  const solved = queries.filter((query) => query.status === 'solved').length
  const unsolved = queries.filter((query) => query.status === 'unsolved').length

  return <div className="student-page">
    <div className="student-welcome-row"><div><div className="student-eyebrow"><span />YOUR ACADEMIC WORKSPACE</div><h1>Good to have you here,<br /><em>{user?.full_name.split(' ')[0] ?? 'Student'}.</em></h1><p>Keep track of your questions and the guidance you receive.</p></div><Link to="/student/queries/new" className="olive-action"><Plus size={17} />Raise a query</Link></div>
    <div className="student-stat-grid" aria-label="Query summary">
      <article className="student-stat-card"><div className="stat-icon stat-icon-olive"><CircleHelp size={17} /></div><span className="stat-label">TOTAL QUERIES</span><strong>{loading || error ? '—' : queries.length}</strong><small>All your submitted questions</small></article>
      <article className="student-stat-card"><div className="stat-icon stat-icon-bronze"><Clock3 size={17} /></div><span className="stat-label">PENDING</span><strong>{loading || error ? '—' : pending}</strong><small>Awaiting a faculty response</small></article>
      <article className="student-stat-card"><div className="stat-icon stat-icon-sage"><Check size={17} /></div><span className="stat-label">SOLVED</span><strong>{loading || error ? '—' : solved}</strong><small>Marked as resolved</small></article>
      <article className="student-stat-card"><div className="stat-icon stat-icon-stone"><CircleHelp size={17} /></div><span className="stat-label">UNSOLVED</span><strong>{loading || error ? '—' : unsolved}</strong><small>Still needing attention</small></article>
    </div>
    {error ? <ErrorBlock message={error} onRetry={() => void loadQueries()} /> : <div className="student-dashboard-grid">
      <section className="student-panel recent-panel"><div className="panel-heading"><div><span className="section-kicker">YOUR INBOX</span><h2>Recent queries</h2></div><Link to="/student/queries" className="subtle-link">View all <ArrowRight size={14} /></Link></div>
        {loading ? <LoadingBlock /> : recentQueries.length === 0 ? <div className="empty-state"><span className="empty-icon"><CircleHelp size={19} /></span><h3>Your questions start here.</h3><p>Raise your first query and the right faculty member can follow up.</p><Link to="/student/queries/new" className="text-action">Raise a query <ArrowRight size={14} /></Link></div> : <div className="query-list">{recentQueries.map((query) => <QueryListItem key={query.id} query={query} />)}</div>}
      </section>
      <aside className="student-quick-panel"><span className="quick-panel-icon"><Sparkles size={18} /></span><span className="section-kicker">MORE WAYS TO GET SUPPORT</span><h2>Make your next question count.</h2><p>Share the details that will help faculty understand what you need.</p><Link to="/student/queries/new" className="quick-panel-link">Start a query <ArrowRight size={15} /></Link><div className="quick-panel-divider" /><div className="future-link"><span className="future-link-icon"><Sparkles size={15} /></span><span><strong>Ask AI</strong><small>Knowledge base answers</small></span><span className="coming-soon-light">COMING SOON</span></div></aside>
    </div>}
    <div className="student-bottom-links"><Link to="/student/queries"><span className="bottom-link-icon"><CircleHelp size={16} /></span><span><strong>My queries</strong><small>Review your conversation history</small></span><ArrowRight size={15} /></Link><Link to="/student/queries/new"><span className="bottom-link-icon"><Plus size={16} /></span><span><strong>Raise a query</strong><small>Ask your faculty for guidance</small></span><ArrowRight size={15} /></Link><div className="disabled-bottom-link"><span className="bottom-link-icon"><Sparkles size={16} /></span><span><strong>Ask AI</strong><small>Coming in a later phase</small></span><span className="coming-soon">SOON</span></div></div>
  </div>
}
