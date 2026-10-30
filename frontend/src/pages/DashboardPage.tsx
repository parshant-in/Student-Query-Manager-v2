import { ArrowRight, ArrowUpRight, Database, LogOut } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import type { UserRole } from '../types/auth'

const roleCopy: Record<Exclude<UserRole, 'student'>, { label: string; title: string; description: string }> = {
  faculty: { label: 'FACULTY WORKSPACE', title: 'A considered space\nfor student support.', description: 'Your faculty workspace is ready. Assigned query tools will appear here as they become available.' },
  admin: { label: 'ADMIN WORKSPACE', title: 'A clear view of\nyour academic system.', description: 'Your admin workspace is ready. Supported system tools will appear here as they become available.' },
}

export function DashboardPage({ role }: { role: Exclude<UserRole, 'student'> }) {
  const { user, logout } = useAuth()
  const copy = roleCopy[role]
  return <div className="dashboard-page">
    <header className="dashboard-header"><a className="dashboard-brand" href={`/${role}/dashboard`}><span className="brand-mark">SQ</span><span>Student Query <b>Manager</b></span></a><div className="dashboard-account"><span className="account-avatar">{user?.full_name.slice(0, 1).toUpperCase()}</span><span className="account-name">{user?.full_name}</span><button className="logout-button" onClick={logout}><LogOut size={16} /><span>Sign out</span></button></div></header>
    <main className="dashboard-main"><div className="dashboard-kicker"><span />{copy.label}</div><h1>{copy.title.split('\n').map((line, index) => <span key={line}>{index === 1 ? <em>{line}</em> : line}<br /></span>)}</h1><p className="dashboard-intro">{copy.description}</p>
      <section className="welcome-card"><div className="welcome-top"><div><span className="section-kicker">YOUR SPACE</span><h2>Welcome, {user?.full_name.split(' ')[0]}.</h2></div><ArrowUpRight size={20} /></div><p>Signed in as <strong>{user?.email}</strong></p>{role === 'admin' && <Link className="admin-kb-link" to="/admin/knowledge-base"><Database size={16} /><span><strong>Knowledge base</strong><small>Manage supporting documents</small></span><ArrowRight size={15} /></Link>}<div className="workspace-rule" /><div className="workspace-foot"><span>Role</span><span className="role-pill">{role}</span></div></section>
      <p className="dashboard-footnote">A thoughtful start to a more connected academic experience.</p>
    </main>
  </div>
}
