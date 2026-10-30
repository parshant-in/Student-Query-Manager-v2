import { AlertCircle, ArrowDownToLine, BookOpenText, Check, FileText, FileUp, Info, LoaderCircle, RefreshCw, Trash2, X } from 'lucide-react'
import { useCallback, useEffect, useRef, useState, type ChangeEvent, type FormEvent } from 'react'
import { ApiError } from '../api/http'
import { documentApi } from '../api/documents'
import { formatDate, LoadingBlock } from '../components/QueryUI'
import { useAuth } from '../context/AuthContext'
import type { DocumentRecord } from '../types/document'

const supportedExtension = /\.(pdf|txt)$/i

function readableError(error: unknown) {
  if (error instanceof ApiError) return error.message
  return 'Check your connection and try again.'
}

export function KnowledgeBasePage() {
  const { token, user } = useAuth()
  const canManage = user?.role === 'faculty' || user?.role === 'admin'
  const fileInput = useRef<HTMLInputElement>(null)
  const [documents, setDocuments] = useState<DocumentRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [libraryError, setLibraryError] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [title, setTitle] = useState('')
  const [fileError, setFileError] = useState('')
  const [uploadError, setUploadError] = useState('')
  const [uploading, setUploading] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [deleteError, setDeleteError] = useState('')
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [selectedDetail, setSelectedDetail] = useState<DocumentRecord | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState('')

  const loadDocuments = useCallback(async () => {
    if (!token) return
    setLoading(true); setLibraryError('')
    try { setDocuments(await documentApi.list(token)) }
    catch (reason) { setLibraryError(readableError(reason)) }
    finally { setLoading(false) }
  }, [token])
  useEffect(() => { void loadDocuments() }, [loadDocuments])

  async function loadDetail(documentId: string) {
    if (!token) return
    setSelectedId(documentId)
    setSelectedDetail(null)
    setDetailError('')
    setDetailLoading(true)
    try { setSelectedDetail(await documentApi.get(token, documentId)) }
    catch (reason) { setDetailError(readableError(reason)) }
    finally { setDetailLoading(false) }
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null
    setFileError(''); setUploadError(''); setFeedback('')
    if (!file) { setSelectedFile(null); return }
    if (!supportedExtension.test(file.name)) {
      setSelectedFile(null)
      setFileError('Choose a PDF or TXT file. These are the formats supported by the knowledge base.')
      event.target.value = ''
      return
    }
    setSelectedFile(file)
  }

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setUploadError(''); setFeedback('')
    if (!selectedFile) { setFileError('Select a PDF or TXT file to upload.'); return }
    if (!supportedExtension.test(selectedFile.name)) { setFileError('Choose a PDF or TXT file.'); return }
    if (!token) { setUploadError('Your session has expired. Please sign in again.'); return }
    setUploading(true)
    try {
      const created = await documentApi.upload(token, selectedFile, title)
      setSelectedFile(null); setTitle(''); setFileError('')
      if (fileInput.current) fileInput.current.value = ''
      setFeedback(`“${created.title}” was uploaded and processed successfully.`)
      await loadDocuments()
    } catch (reason) {
      setUploadError(readableError(reason))
    } finally { setUploading(false) }
  }

  async function handleDelete(document: DocumentRecord) {
    if (!canManage || !token || deletingId) return
    const confirmed = window.confirm(`Delete “${document.title}” (${document.filename})? The backend removes the stored file and library record. Its indexed RAG chunks may remain.`)
    if (!confirmed) return
    setDeleteError(''); setFeedback(''); setDeletingId(document.id)
    try {
      await documentApi.delete(token, document.id)
      setFeedback(`“${document.title}” was deleted from the library. Associated RAG chunks may remain.`)
      if (selectedId === document.id) { setSelectedId(null); setSelectedDetail(null) }
      await loadDocuments()
    } catch (reason) { setDeleteError(readableError(reason)) }
    finally { setDeletingId(null) }
  }

  return <div className="student-page knowledge-base-page">
    <div className="student-welcome-row kb-heading-row"><div><div className="student-eyebrow"><span />ACADEMIC RESOURCES</div><h1>Knowledge base</h1><p>Manage the documents used to support grounded answers.</p></div>{canManage && <div className="kb-document-count"><BookOpenText size={16} /><span>{loading ? 'Loading library' : `${documents.length} ${documents.length === 1 ? 'document' : 'documents'}`}</span></div>}</div>

    {canManage && <section className="student-panel kb-upload-panel"><div className="kb-section-heading"><span className="form-panel-icon"><FileUp size={18} /></span><div><span className="section-kicker">ADD TO THE LIBRARY</span><h2>Upload a document</h2><p>PDF and plain text files are supported.</p></div></div>
      <div className="kb-processing-note"><Info size={15} /><p>Documents are processed during upload. Larger files may take a little time; the upload will finish once ingestion is complete.</p></div>
      <form className="kb-upload-form" onSubmit={handleUpload}>
        <div className="kb-file-field"><label className="query-field-label" htmlFor="kb-file">Document file <span>PDF or TXT</span></label><input ref={fileInput} id="kb-file" className="kb-file-input" type="file" accept=".pdf,.txt,application/pdf,text/plain" onChange={handleFileChange} disabled={uploading} aria-describedby="kb-file-hint" /><small id="kb-file-hint">Choose one PDF or TXT file. Text extraction and indexing happen synchronously on the backend.</small>{selectedFile && <div className="selected-file"><FileText size={15} /><span>{selectedFile.name}</span><small>{(selectedFile.size / 1024).toFixed(0)} KB</small><button type="button" onClick={() => { setSelectedFile(null); setFileError(''); if (fileInput.current) fileInput.current.value = '' }} disabled={uploading} aria-label="Remove selected file"><X size={14} /></button></div>}{fileError && <p className="kb-error-text" role="alert">{fileError}</p>}</div>
        <div className="kb-title-field"><label className="query-field-label" htmlFor="kb-title">Display title <span>Optional</span></label><input id="kb-title" className="query-text-input" type="text" maxLength={200} value={title} onChange={(event) => setTitle(event.target.value)} placeholder={selectedFile?.name || 'Defaults to the filename'} disabled={uploading} /><small>If left blank, the backend uses the filename.</small></div>
        {uploadError && <div className="form-alert kb-full-row" role="alert">{uploadError}</div>}
        {feedback && <div className="success-alert kb-full-row" role="status"><Check size={14} />{feedback}</div>}
        <div className="kb-submit-row"><button className="olive-action" type="submit" disabled={uploading || !selectedFile}>{uploading ? <><LoaderCircle className="spin-icon" size={15} />Uploading &amp; processing…</> : <>Upload document <ArrowDownToLine size={15} /> </>}</button></div>
      </form>
    </section>}

    <section className="student-panel kb-library-panel"><div className="kb-library-heading"><div><span className="section-kicker">DOCUMENT LIBRARY</span><h2>Knowledge base documents</h2><p>Documents currently registered with the backend.</p></div><button type="button" className="icon-button" onClick={() => void loadDocuments()} disabled={loading} aria-label="Refresh document library" title="Refresh"><RefreshCw size={15} className={loading ? 'spin-icon' : ''} /></button></div>
      <div className="kb-rag-caveat"><Info size={14} /><span>Deleting a library item removes its file and database record. The current backend does not remove its chunks from ChromaDB.</span></div>
      {deleteError && <div className="form-alert kb-list-alert" role="alert">{deleteError}</div>}
      {loading ? <LoadingBlock label="Loading the document library…" /> : libraryError ? <div className="kb-library-state"><div className="error-state-icon"><AlertCircle size={18} /></div><h3>Library unavailable</h3><p>{libraryError}</p><button className="text-action" type="button" onClick={() => void loadDocuments()}>Try again <RefreshCw size={13} /></button></div> : documents.length === 0 ? <div className="kb-library-state"><span className="empty-icon"><BookOpenText size={19} /></span><h3>No documents yet.</h3><p>Once a supported PDF or TXT file is uploaded and processed, it will appear here.</p></div> : <div className="kb-document-list">{documents.map((document) => <article className="kb-document-row" key={document.id}>
        <span className="kb-doc-icon"><FileText size={18} /></span><div className="kb-doc-main"><h3>{document.title}</h3><p>{document.filename}</p><div className="kb-doc-meta"><span>Added {formatDate(document.created_at, true)}</span><span>ID · {document.id.slice(0, 8)}</span></div></div><div className="kb-doc-actions"><button className="kb-secondary-button" type="button" onClick={() => selectedId === document.id ? (setSelectedId(null), setSelectedDetail(null)) : void loadDetail(document.id)} aria-expanded={selectedId === document.id}>{selectedId === document.id ? 'Close details' : 'Details'}</button>{canManage && <button className="kb-delete-button" type="button" onClick={() => void handleDelete(document)} disabled={deletingId !== null} aria-label={`Delete ${document.title}`} title="Delete document">{deletingId === document.id ? <LoaderCircle size={15} className="spin-icon" /> : <Trash2 size={15} />}</button>}</div>
        {selectedId === document.id && <div className="kb-detail-panel">{detailLoading ? <span className="kb-detail-loading"><LoaderCircle size={14} className="spin-icon" />Loading document details…</span> : detailError ? <p className="kb-error-text" role="alert">{detailError}</p> : selectedDetail && <><div><span>DOCUMENT ID</span><strong>{selectedDetail.id}</strong></div><div><span>UPLOADED BY</span><strong>{selectedDetail.uploaded_by}</strong></div><div><span>FILENAME</span><strong>{selectedDetail.filename}</strong></div><div><span>ADDED</span><strong>{formatDate(selectedDetail.created_at, true)}</strong></div></>}</div>}
      </article>)}</div>}
    </section>
  </div>
}
