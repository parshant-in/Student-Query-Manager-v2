import { ArrowRight, Clock3, MessageSquareText } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { QueryResponse, QueryStatus } from '../types/query'

export function formatDate(value: string, includeTime = false) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Date unavailable'
  return new Intl.DateTimeFormat(undefined, includeTime
    ? { dateStyle: 'medium', timeStyle: 'short' }
    : { dateStyle: 'medium' }).format(date)
}

export function StatusBadge({ status }: { status: QueryStatus }) {
  return <span className={`query-status status-${status}`}><span />{status}</span>
}

export function QueryListItem({ query, to = `/student/queries/${query.id}`, metadata }: { query: QueryResponse; to?: string; metadata?: string }) {
  return <Link className="query-list-item" to={to}>
    <div className="query-item-main"><div className="query-item-title-row"><h3>{query.title}</h3><StatusBadge status={query.status} /></div><p>{query.description}</p><div className="query-item-meta"><span><Clock3 size={13} />Created {formatDate(query.created_at)}</span><span><MessageSquareText size={13} />Updated {formatDate(query.updated_at)}</span>{metadata && <span>{metadata}</span>}</div></div>
    <ArrowRight size={17} className="query-item-arrow" />
  </Link>
}

export function LoadingBlock({ label = 'Loading your queries…' }: { label?: string }) {
  return <div className="query-state"><span className="loading-mark" /><p>{label}</p></div>
}

export function ErrorBlock({ message, onRetry }: { message: string; onRetry: () => void }) {
  return <div className="query-error" role="alert"><div><strong>We couldn’t load this just now.</strong><p>{message}</p></div><button type="button" className="text-action" onClick={onRetry}>Try again <ArrowRight size={14} /></button></div>
}
