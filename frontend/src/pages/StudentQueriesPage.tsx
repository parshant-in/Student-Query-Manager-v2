import { ArrowRight, CircleHelp, Plus } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ApiError } from '../api/http'
import { queryApi } from '../api/queries'
import { ErrorBlock, LoadingBlock, QueryListItem } from '../components/QueryUI'
import { useAuth } from '../context/AuthContext'
import type { QueryResponse } from '../types/query'

function messageFor(error: unknown) {
  return error instanceof ApiError ? error.message : 'Check your connection and try again.'
}

export function StudentQueriesPage() {
  const { token } = useAuth()
  const [queries, setQueries] = useState<QueryResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const loadQueries = useCallback(async () => {
    if (!token) return
    setLoading(true); setError('')
    try { setQueries(await queryApi.listMine(token)) }
    catch (reason) { setError(messageFor(reason)) }
    finally { setLoading(false) }
  }, [token])
  useEffect(() => { void loadQueries() }, [loadQueries])

  return <div className="student-page">
    <div className="page-heading-row"><div><div className="student-eyebrow"><span />YOUR CONVERSATIONS</div><h1>My queries</h1><p>Every question you’ve raised, all in one place.</p></div><Link to="/student/queries/new" className="olive-action"><Plus size={17} />Raise a query</Link></div>
    <section className="student-panel queries-page-panel"><div className="panel-heading"><div><span className="section-kicker">QUERY HISTORY</span><h2>{loading ? 'Your questions' : `${queries.length} ${queries.length === 1 ? 'question' : 'questions'}`}</h2></div></div>
      {error ? <ErrorBlock message={error} onRetry={() => void loadQueries()} /> : loading ? <LoadingBlock /> : queries.length === 0 ? <div className="empty-state"><span className="empty-icon"><CircleHelp size={19} /></span><h3>No queries yet.</h3><p>When you raise a query, it will appear here with its status and updates.</p><Link to="/student/queries/new" className="text-action">Create your first query <ArrowRight size={14} /></Link></div> : <div className="query-list">{[...queries].sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at)).map((query) => <QueryListItem key={query.id} query={query} />)}</div>}
    </section>
  </div>
}
