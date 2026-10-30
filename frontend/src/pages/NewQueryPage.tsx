import { ArrowLeft, ArrowRight, BookOpenText, ChevronDown } from 'lucide-react'
import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ApiError } from '../api/http'
import { queryApi } from '../api/queries'
import { useAuth } from '../context/AuthContext'
import type { Category } from '../types/query'

export function NewQueryPage() {
  const { token } = useAuth()
  const navigate = useNavigate()
  const [categories, setCategories] = useState<Category[]>([])
  const [categoriesLoading, setCategoriesLoading] = useState(true)
  const [categoryError, setCategoryError] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const loadCategories = useCallback(async () => {
    if (!token) return
    setCategoriesLoading(true); setCategoryError('')
    try { setCategories(await queryApi.listCategories(token)) }
    catch (reason) { setCategoryError(reason instanceof ApiError ? reason.message : 'Check your connection and try again.') }
    finally { setCategoriesLoading(false) }
  }, [token])
  useEffect(() => { void loadCategories() }, [loadCategories])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError('')
    if (!categoryId) { setError('Choose a category for your query.'); return }
    if (!title.trim() || !description.trim()) { setError('Add a title and description before submitting.'); return }
    if (!token) { setError('Your session has expired. Please sign in again.'); return }
    setSubmitting(true)
    try {
      const query = await queryApi.create(token, { category_id: categoryId, title: title.trim(), description: description.trim() })
      navigate(`/student/queries/${query.id}`, { replace: true })
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : 'We could not submit your query. Please try again.')
    } finally { setSubmitting(false) }
  }

  return <div className="student-page narrow-student-page">
    <Link to="/student/dashboard" className="back-link"><ArrowLeft size={15} />Back to overview</Link>
    <div className="student-eyebrow"><span />ASK FOR GUIDANCE</div><h1 className="form-page-title">Raise a query</h1><p className="form-page-intro">Tell us what you need help with. Your query will be routed to the relevant faculty member.</p>
    <section className="student-panel query-form-panel"><div className="form-panel-heading"><span className="form-panel-icon"><BookOpenText size={18} /></span><div><span className="section-kicker">NEW CONVERSATION</span><h2>A little context goes a long way.</h2></div></div>
      <form className="student-query-form" onSubmit={handleSubmit} noValidate>
        {error && <div className="form-alert" role="alert">{error}</div>}
        <label className="query-field-label" htmlFor="category">Category <span>Required</span></label>
        <div className="select-wrap"><select id="category" value={categoryId} onChange={(event) => setCategoryId(event.target.value)} disabled={categoriesLoading || !!categoryError} required><option value="">{categoriesLoading ? 'Loading categories…' : categoryError ? 'Categories unavailable' : 'Choose a category'}</option>{categories.map((category) => <option value={category.id} key={category.id}>{category.name}</option>)}</select><ChevronDown size={16} /></div>
        {categoryError ? <div className="inline-error" role="alert"><span>{categoryError}</span><button className="text-action" type="button" onClick={() => void loadCategories()}>Retry <ArrowRight size={13} /></button></div> : categories.length > 0 && categoryId ? <p className="field-description">{categories.find((category) => category.id === categoryId)?.description}</p> : null}
        {!categoriesLoading && !categoryError && categories.length === 0 && <p className="inline-empty">There are no categories available right now, so a query can’t be submitted.</p>}
        <label className="query-field-label" htmlFor="query-title">Title <span>Required</span></label>
        <input className="query-text-input" id="query-title" value={title} onChange={(event) => setTitle(event.target.value)} maxLength={200} placeholder="A short summary of your question" required />
        <div className="field-bottom-note"><span>Keep it clear and specific.</span><span>{title.length}/200</span></div>
        <label className="query-field-label" htmlFor="query-description">Description <span>Required</span></label>
        <textarea className="query-textarea" id="query-description" value={description} onChange={(event) => setDescription(event.target.value)} maxLength={5000} rows={7} placeholder="Share the details that will help faculty understand your question…" required />
        <div className="field-bottom-note"><span>Include any useful context or what you’ve tried.</span><span>{description.length}/5000</span></div>
        <div className="query-form-actions"><Link to="/student/dashboard" className="cancel-link">Cancel</Link><button className="olive-action" type="submit" disabled={submitting || categoriesLoading || Boolean(categoryError) || categories.length === 0}>{submitting ? <><span className="button-spinner" />Submitting…</> : <>Submit query <ArrowRight size={16} /></>}</button></div>
      </form>
    </section>
  </div>
}
