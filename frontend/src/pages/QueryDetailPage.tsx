import { ArrowLeft, Clock3, MessageSquareText } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ApiError } from '../api/http'
import { queryApi } from '../api/queries'
import { formatDate, LoadingBlock, StatusBadge } from '../components/QueryUI'
import { useAuth } from '../context/AuthContext'
import type { QueryDetail } from '../types/query'

export function QueryDetailPage() {
  const { queryId = '' } = useParams()
  const { token } = useAuth()
  const [query, setQuery] = useState<QueryDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const loadQuery = useCallback(async () => {
    if (!token) return
    setLoading(true); setError('')
    try { setQuery(await queryApi.getMine(token, queryId)) }
    catch (reason) {
      setQuery(null)
      setError(reason instanceof ApiError && reason.status === 404 ? 'This query could not be found or is no longer available.' : reason instanceof ApiError ? reason.message : 'Check your connection and try again.')
    } finally { setLoading(false) }
  }, [token, queryId])
  useEffect(() => { void loadQuery() }, [loadQuery])

  if (loading) return <div className="student-page"><Link to="/student/queries" className="back-link"><ArrowLeft size={15} />Back to my queries</Link><LoadingBlock label="Loading query details…" /></div>
  if (error || !query) return <div className="student-page"><Link to="/student/queries" className="back-link"><ArrowLeft size={15} />Back to my queries</Link><section className="student-panel detail-error-panel"><div className="empty-icon">!</div><h2>We couldn’t open this query.</h2><p>{error || 'This query is not available.'}</p><button type="button" className="text-action" onClick={() => void loadQuery()}>Try again <span>→</span></button></section></div>

  return <div className="student-page detail-page">
    <Link to="/student/queries" className="back-link"><ArrowLeft size={15} />Back to my queries</Link>
    <div className="detail-heading"><div className="student-eyebrow"><span />QUERY DETAILS</div><div className="detail-title-row"><h1>{query.title}</h1><StatusBadge status={query.status} /></div><div className="detail-meta"><span><Clock3 size={14} />Submitted {formatDate(query.created_at, true)}</span><span>Last updated {formatDate(query.updated_at, true)}</span></div></div>
    <section className="student-panel query-description-panel"><div className="detail-section-heading"><span className="section-kicker">YOUR QUESTION</span><span className="detail-id">QUERY · {query.id.slice(0, 8).toUpperCase()}</span></div><p className="query-full-description">{query.description}</p></section>
    <section className="responses-section"><div className="panel-heading"><div><span className="section-kicker">FACULTY FOLLOW-UP</span><h2>Responses <span className="response-count">{query.responses.length}</span></h2></div></div>
      {query.responses.length === 0 ? <div className="student-panel response-empty"><span className="empty-icon"><MessageSquareText size={18} /></span><h3>No response yet.</h3><p>Your faculty response will appear here. You can return later to check for updates.</p></div> : <div className="response-list">{query.responses.map((response) => <article className="student-panel faculty-response-card" key={response.id}><div className="response-card-heading"><span className="response-avatar"><MessageSquareText size={16} /></span><div><strong>Faculty response</strong><span>{formatDate(response.created_at, true)}</span></div></div><p>{response.message}</p></article>)}</div>}
    </section>
  </div>
}
