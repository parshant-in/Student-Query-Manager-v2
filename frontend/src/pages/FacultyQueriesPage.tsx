import { CircleHelp, Filter } from 'lucide-react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { ApiError } from '../api/http'
import { facultyApi } from '../api/faculty'
import { ErrorBlock, LoadingBlock, QueryListItem } from '../components/QueryUI'
import { useAuth } from '../context/AuthContext'
import type { QueryResponse, QueryStatus } from '../types/query'

type StatusFilter = QueryStatus | 'all'
const filters: { key: StatusFilter; label: string }[] = [
  { key: 'all', label: 'All queries' },
  { key: 'pending', label: 'Pending' },
  { key: 'solved', label: 'Solved' },
  { key: 'unsolved', label: 'Unsolved' },
]

export function FacultyQueriesPage() {
  const { token } = useAuth()
  const [queries, setQueries] = useState<QueryResponse[]>([])
  const [filter, setFilter] = useState<StatusFilter>('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const loadQueries = useCallback(async () => {
    if (!token) return
    setLoading(true); setError('')
    try { setQueries(await facultyApi.listAssigned(token)) }
    catch (reason) { setError(reason instanceof ApiError ? reason.message : 'Check your connection and try again.') }
    finally { setLoading(false) }
  }, [token])
  useEffect(() => { void loadQueries() }, [loadQueries])

  const filteredQueries = useMemo(() => [...queries]
    .filter((query) => filter === 'all' || query.status === filter)
    .sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at)), [queries, filter])

  return <div className="student-page">
    <div className="page-heading-row"><div><div className="student-eyebrow"><span />FACULTY INBOX</div><h1>Department queries</h1><p>Review your department’s queue and claim a query before responding.</p></div></div>
    <section className="student-panel faculty-queries-panel"><div className="faculty-filter-header"><div><span className="section-kicker">DEPARTMENT QUEUE</span><h2>{loading ? 'Department queries' : `${queries.length} ${queries.length === 1 ? 'query' : 'queries'}`}</h2></div><span className="filter-label"><Filter size={14} />Filter by status</span></div>
      <div className="status-filter-row" role="group" aria-label="Filter queries by status">{filters.map(({ key, label }) => <button type="button" key={key} className={`status-filter${filter === key ? ' active' : ''}`} aria-pressed={filter === key} onClick={() => setFilter(key)}>{label}{key !== 'all' && <span>{queries.filter((query) => query.status === key).length}</span>}</button>)}</div>
      {error ? <div className="faculty-list-state"><ErrorBlock message={error} onRetry={() => void loadQueries()} /></div> : loading ? <LoadingBlock label="Loading department queries…" /> : filteredQueries.length === 0 ? <div className="empty-state faculty-empty"><span className="empty-icon"><CircleHelp size={19} /></span><h3>{queries.length === 0 ? 'No department queries yet.' : `No ${filter} queries.`}</h3><p>{queries.length === 0 ? 'Select your department from the faculty dashboard. New queries will appear in this queue.' : 'Try another status filter to see other queries.'}</p>{queries.length > 0 && filter !== 'all' && <button type="button" className="text-action" onClick={() => setFilter('all')}>Show all queries</button>}</div> : <div className="query-list">{filteredQueries.map((query) => <QueryListItem key={query.id} query={query} to={`/faculty/queries/${query.id}`} metadata={`Category ID · ${query.category_id.slice(0, 8)} · ${query.faculty_id ? 'Claimed' : 'Available to claim'}`} />)}</div>}
    </section>
    <p className="faculty-list-note">Queries remain available to the department until one faculty member claims them. Claiming is exclusive.</p>
  </div>
}
