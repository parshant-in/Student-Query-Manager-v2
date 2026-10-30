import { BookOpenText, FileText, MessageCircleQuestion, RotateCcw, Send, Sparkles } from 'lucide-react'
import { useState, type FormEvent } from 'react'
import { ApiError } from '../api/http'
import { ragApi } from '../api/rag'
import { useAuth } from '../context/AuthContext'
import type { RagAskResponse } from '../types/rag'

function errorMessage(error: unknown) {
  if (error instanceof ApiError) {
    if (error.status === 401) return 'Your session has expired. Please sign in again.'
    if (error.status === 403) return 'Ask AI is available to student accounts.'
    if (error.status === 503) return 'The answer service is not configured right now. Please try again later.'
    if (error.status === 502) return 'The answer service could not generate a response. Please try again shortly.'
    return error.message
  }
  return 'We could not reach the answer service. Check your connection and try again.'
}

export function AskAIPage() {
  const { token } = useAuth()
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState<RagAskResponse | null>(null)
  const [error, setError] = useState('')
  const [validationError, setValidationError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(''); setValidationError('')
    const trimmedQuestion = question.trim()
    if (!trimmedQuestion) { setValidationError('Enter a question before asking.'); return }
    if (!token) { setError('Your session has expired. Please sign in again.'); return }
    setSubmitting(true)
    setResult(null)
    try {
      setResult(await ragApi.ask(token, { question: trimmedQuestion }))
    } catch (reason) {
      setError(errorMessage(reason))
    } finally { setSubmitting(false) }
  }

  function askAnother() {
    setQuestion(''); setResult(null); setError(''); setValidationError('')
    document.getElementById('rag-question')?.focus()
  }

  return <div className="student-page ask-ai-page">
    <div className="student-eyebrow"><span />KNOWLEDGE-BASE ASSISTANT</div>
    <div className="ask-ai-heading"><div><h1>Ask AI</h1><p>Ask an academic question and get an answer grounded in the knowledge base.</p></div><span className="ask-ai-emblem"><Sparkles size={21} /></span></div>

    <section className="student-panel ask-ai-composer-panel">
      <div className="ask-ai-composer-heading"><span className="ask-ai-question-icon"><MessageCircleQuestion size={17} /></span><div><span className="section-kicker">YOUR QUESTION</span><h2>What would you like to know?</h2></div></div>
      <form className="ask-ai-form" onSubmit={handleSubmit} noValidate>
        <label className="visually-hidden" htmlFor="rag-question">Your academic question</label>
        <textarea id="rag-question" className="query-textarea ask-ai-textarea" rows={4} maxLength={2000} value={question} onChange={(event) => { setQuestion(event.target.value); setValidationError(''); setError('') }} placeholder="For example: What documents do I need to submit for…" disabled={submitting} aria-describedby="rag-question-hint" />
        <div className="ask-ai-form-footer"><span id="rag-question-hint">Answers use information found in the available knowledge base.</span><span>{question.length}/2000</span></div>
        {(validationError || error) && <div className="form-alert ask-ai-alert" role="alert">{validationError || error}</div>}
        <div className="ask-ai-submit-row"><span className="ask-ai-privacy-note"><BookOpenText size={14} />Grounded in indexed academic documents</span><button className="olive-action" type="submit" disabled={submitting}>{submitting ? <><span className="button-spinner" />Thinking…</> : <>Ask question <Send size={14} /></>}</button></div>
      </form>
    </section>

    {submitting && <section className="student-panel ask-ai-loading-panel" aria-live="polite"><span className="loading-mark" /><div><strong>Looking through the knowledge base…</strong><p>This may take a little while while your question is retrieved and answered.</p></div></section>}

    {!submitting && result && <section className="ask-ai-result-area" aria-live="polite">
      <article className="student-panel ask-ai-answer-card"><div className="ask-ai-answer-heading"><span className="ask-ai-answer-icon"><Sparkles size={16} /></span><div><span className="section-kicker">ANSWER</span><h2>Here’s what I found</h2></div></div><div className="ask-ai-question-summary"><span>YOU ASKED</span><p>{question.trim()}</p></div><p className="ask-ai-answer-text">{result.answer}</p></article>
      {result.sources.length > 0 && <section className="ask-ai-sources-section"><div className="ask-ai-sources-heading"><div><span className="section-kicker">REFERENCE MATERIAL</span><h2>Sources from the knowledge base</h2></div><span className="source-count">{result.sources.length} {result.sources.length === 1 ? 'source' : 'sources'}</span></div><div className="ask-ai-source-list">{result.sources.map((source, index) => <article className="student-panel ask-ai-source-card" key={`${source.document_id}-${index}`}><span className="kb-doc-icon"><FileText size={18} /></span><div className="ask-ai-source-main"><h3>{source.title}</h3><p>{source.filename}</p><div className="ask-ai-source-meta"><span>Document · {source.document_id}</span><span>Match distance · {Number.isFinite(source.score) ? source.score.toFixed(3) : source.score}</span></div></div></article>)}</div><p className="source-score-note">Match distance is returned by the backend; lower values indicate closer matches.</p></section>}
      <div className="ask-ai-another-row"><span>Have another question?</span><button className="text-action" type="button" onClick={askAnother}>Ask another <RotateCcw size={13} /></button></div>
    </section>}

    {!submitting && !result && !error && <section className="student-panel ask-ai-empty-state"><span className="ask-ai-empty-icon"><Sparkles size={20} /></span><h2>Your knowledge base, ready to help.</h2><p>Ask a question to receive an answer from indexed documents. Sources will appear with the answer when the backend returns them.</p><div className="ask-ai-empty-rule"><span /><small>ANSWERS ARE GENERATED BY THE ACADEMIC ASSISTANT</small><span /></div></section>}
    {!submitting && error && !result && <p className="ask-ai-retry-note">You can retry by submitting your question again.</p>}
  </div>
}
