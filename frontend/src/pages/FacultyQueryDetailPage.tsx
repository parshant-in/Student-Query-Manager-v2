import { ArrowLeft, Check, Clock3, MessageSquareText, Send } from 'lucide-react'
import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ApiError } from '../api/http'
import { facultyApi } from '../api/faculty'
import { formatDate, LoadingBlock, StatusBadge } from '../components/QueryUI'
import { useAuth } from '../context/AuthContext'
import type { QueryDetail, QueryStatus } from '../types/query'

const statusChoices: { value: QueryStatus; label: string }[] = [
  { value: 'pending', label: 'Pending' },
  { value: 'solved', label: 'Solved' },
  { value: 'unsolved', label: 'Unsolved' },
]
const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

export function FacultyQueryDetailPage() {
  const { queryId = '' } = useParams()
  const { token, user } = useAuth()
  const [query, setQuery] = useState<QueryDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [responseBusy, setResponseBusy] = useState(false)
  const [responseFeedback, setResponseFeedback] = useState('')
  const [responseError, setResponseError] = useState('')
  const [nextStatus, setNextStatus] = useState<QueryStatus>('pending')
  const [statusBusy, setStatusBusy] = useState(false)
  const [statusFeedback, setStatusFeedback] = useState('')
  const [statusError, setStatusError] = useState('')
  const [claimBusy, setClaimBusy] = useState(false)
  const [claimError, setClaimError] = useState('')
  const [claimFeedback, setClaimFeedback] = useState('')

  const loadQuery = useCallback(async () => {
    setLoading(true); setError('')
    if (!uuidPattern.test(queryId)) {
      setQuery(null)
      setError('This link does not contain a valid query ID.')
      setLoading(false)
      return
    }
    if (!token) { setQuery(null); setError('Your session has expired. Please sign in again.'); setLoading(false); return }
    try {
      const result = await facultyApi.getAssigned(token, queryId)
      setQuery(result)
      setNextStatus(result.status)
    } catch (reason) {
      setQuery(null)
      if (reason instanceof ApiError && reason.status === 404) setError('This query was not found in your assigned queue.')
      else if (reason instanceof ApiError) setError(reason.message)
      else setError('Check your connection and try again.')
    } finally { setLoading(false) }
  }, [token, queryId])
  useEffect(() => { void loadQuery() }, [loadQuery])

  async function handleResponse(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setResponseError(''); setResponseFeedback('')
    const trimmedMessage = message.trim()
    if (!trimmedMessage) { setResponseError('Write a response before submitting.'); return }
    if (!token) { setResponseError('Your session has expired. Please sign in again.'); return }
    setResponseBusy(true)
    try {
      await facultyApi.respond(token, queryId, { message: trimmedMessage })
      setMessage('')
      setResponseFeedback('Your response was sent.')
      await loadQuery()
    } catch (reason) {
      setResponseError(reason instanceof ApiError ? reason.message : 'We could not send your response. Please try again.')
    } finally { setResponseBusy(false) }
  }

  async function handleStatusUpdate() {
    setStatusError(''); setStatusFeedback('')
    if (!token || !query) { setStatusError('Your session has expired. Please sign in again.'); return }
    if (nextStatus === query.status) return
    setStatusBusy(true)
    try {
      const updated = await facultyApi.updateStatus(token, queryId, { status: nextStatus })
      setQuery((current) => current ? { ...current, status: updated.status, updated_at: updated.updated_at } : current)
      setNextStatus(updated.status)
      setStatusFeedback('Query status updated.')
    } catch (reason) {
      setStatusError(reason instanceof ApiError ? reason.message : 'We could not update the status. Please try again.')
    } finally { setStatusBusy(false) }
  }

  async function handleClaim() {
    if (!token) { setClaimError('Your session has expired. Please sign in again.'); return }
    setClaimBusy(true); setClaimError(''); setClaimFeedback('')
    try {
      await facultyApi.claim(token, queryId)
      await loadQuery()
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 409) {
        setClaimFeedback('This query has already been claimed by another faculty member.')
        await loadQuery()
      } else {
        setClaimError(reason instanceof ApiError ? reason.message : 'We could not claim this query. Refresh and try again.')
      }
    } finally { setClaimBusy(false) }
  }

  if (loading) return <div className="student-page"><Link to="/faculty/queries" className="back-link"><ArrowLeft size={15} />Back to assigned queries</Link><LoadingBlock label="Loading assigned query…" /></div>
  if (error || !query) return <div className="student-page"><Link to="/faculty/queries" className="back-link"><ArrowLeft size={15} />Back to assigned queries</Link><section className="student-panel detail-error-panel"><div className="empty-icon">!</div><h2>We couldn’t open this query.</h2><p>{error || 'This query is not available.'}</p><button type="button" className="text-action" onClick={() => void loadQuery()}>Try again <span>→</span></button></section></div>

  return <div className="student-page detail-page faculty-detail-page">
    <Link to="/faculty/queries" className="back-link"><ArrowLeft size={15} />Back to assigned queries</Link>
    <div className="detail-heading"><div className="student-eyebrow"><span />ASSIGNED QUERY</div><div className="detail-title-row"><h1>{query.title}</h1><StatusBadge status={query.status} /></div><div className="detail-meta"><span><Clock3 size={14} />Submitted {formatDate(query.created_at, true)}</span><span>Last updated {formatDate(query.updated_at, true)}</span></div></div>
    <div className="faculty-meta-strip"><div><span>STUDENT ID</span><strong>{query.student_id}</strong></div><div><span>CATEGORY ID</span><strong>{query.category_id}</strong></div><div><span>QUERY ID</span><strong>{query.id}</strong></div></div>
    <section className="student-panel query-description-panel"><div className="detail-section-heading"><span className="section-kicker">STUDENT QUESTION</span><span className="detail-id">DESCRIPTION</span></div><p className="query-full-description">{query.description}</p></section>

    {query.faculty_id === null && <section className="student-panel faculty-claim-panel"><div><span className="section-kicker">DEPARTMENT QUEUE</span><h2>This query is available to claim.</h2><p>Claiming assigns it to you so another faculty member cannot respond to the same query.</p></div><button className="olive-action" type="button" onClick={() => void handleClaim()} disabled={claimBusy}>{claimBusy ? <><span className="button-spinner" />Claiming…</> : 'Claim query'}</button>{claimError && <p className="inline-feedback feedback-error" role="alert">{claimError}</p>}</section>}
    {query.faculty_id !== user?.id && query.faculty_id !== null && <section className="student-panel faculty-claim-panel"><div><span className="section-kicker">DEPARTMENT QUEUE</span><h2>Claimed by another faculty member</h2><p>Only the faculty member who claimed it can respond or update its status.</p></div>{claimFeedback && <p className="inline-feedback" role="status">{claimFeedback}</p>}</section>}

    {query.faculty_id === user?.id && <section className="student-panel faculty-status-panel"><div><span className="section-kicker">WORKFLOW</span><h2>Update query status</h2><p>Choose the current state of this query.</p></div><div className="status-update-controls"><label className="visually-hidden" htmlFor="query-status">Query status</label><select id="query-status" value={nextStatus} onChange={(event) => { setNextStatus(event.target.value as QueryStatus); setStatusFeedback(''); setStatusError('') }} disabled={statusBusy}>{statusChoices.map((choice) => <option value={choice.value} key={choice.value}>{choice.label}</option>)}</select><button className="olive-action" type="button" onClick={() => void handleStatusUpdate()} disabled={statusBusy || nextStatus === query.status}>{statusBusy ? <><span className="button-spinner" />Saving…</> : <><Check size={15} />Save status</>}</button></div>{(statusError || statusFeedback) && <p className={`inline-feedback${statusError ? ' feedback-error' : ''}`} role={statusError ? 'alert' : 'status'}>{statusError || statusFeedback}</p>}</section>}

    <section className="responses-section"><div className="panel-heading"><div><span className="section-kicker">CONVERSATION</span><h2>Responses <span className="response-count">{query.responses.length}</span></h2></div></div>
      {query.responses.length === 0 ? <div className="student-panel response-empty"><span className="empty-icon"><MessageSquareText size={18} /></span><h3>No response has been sent yet.</h3><p>Your response will appear here after it is submitted.</p></div> : <div className="response-list">{query.responses.map((response) => <article className="student-panel faculty-response-card" key={response.id}><div className="response-card-heading"><span className="response-avatar"><MessageSquareText size={16} /></span><div><strong>{response.faculty_id === user?.id ? 'Your response' : 'Faculty response'}</strong><span>{formatDate(response.created_at, true)}</span></div></div><p>{response.message}</p></article>)}</div>}
    </section>

    {query.faculty_id === user?.id && <section className="student-panel faculty-composer-panel"><div className="composer-heading"><span className="form-panel-icon"><MessageSquareText size={17} /></span><div><span className="section-kicker">REPLY TO STUDENT</span><h2>Write a helpful response.</h2></div></div>
      <form className="student-query-form" onSubmit={handleResponse} noValidate>{responseError && <div className="form-alert" role="alert">{responseError}</div>}{responseFeedback && <div className="success-alert" role="status">{responseFeedback}</div>}<label className="query-field-label" htmlFor="faculty-response">Your response <span>Required</span></label><textarea className="query-textarea" id="faculty-response" value={message} onChange={(event) => setMessage(event.target.value)} maxLength={5000} rows={6} placeholder="Share clear guidance or the next steps for the student…" required /><div className="field-bottom-note"><span>Responses are visible in the student’s query details.</span><span>{message.length}/5000</span></div><div className="query-form-actions"><button className="olive-action" type="submit" disabled={responseBusy || !message.trim()}>{responseBusy ? <><span className="button-spinner" />Sending…</> : <>Send response <Send size={14} /></>}</button></div></form>
    </section>}
  </div>
}
