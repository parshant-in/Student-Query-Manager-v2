import { ArrowLeft, BookOpenCheck, LogOut } from 'lucide-react'
import { Link } from 'react-router-dom'
import { KnowledgeBasePage } from './KnowledgeBasePage'
import { useAuth } from '../context/AuthContext'

export function AdminKnowledgeBasePage() {
  const { user, logout } = useAuth()
  return <div className="admin-kb-shell">
    <header className="admin-kb-header"><Link to="/admin/dashboard" className="dashboard-brand"><span className="brand-mark"><BookOpenCheck size={18} /></span><span>Student Query <b>Manager</b></span></Link><div className="dashboard-account"><span className="account-name">{user?.full_name}</span><Link className="admin-kb-back" to="/admin/dashboard"><ArrowLeft size={14} />Dashboard</Link><button className="logout-button" type="button" onClick={logout}><LogOut size={15} /><span>Sign out</span></button></div></header>
    <main className="admin-kb-main"><KnowledgeBasePage /></main>
    <footer className="student-footer"><span>Student Query Manager</span><span>Admin workspace</span></footer>
  </div>
}
