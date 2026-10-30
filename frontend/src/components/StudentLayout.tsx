import { ArrowUpRight, BookOpenCheck, CircleHelp, LayoutDashboard, LogOut, Plus, Sparkles } from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const navItems = [
  { to: '/student/dashboard', label: 'Overview', icon: LayoutDashboard, end: true },
  { to: '/student/queries', label: 'My queries', icon: CircleHelp, end: false },
]

export function StudentLayout() {
  const { user, logout } = useAuth()
  return <div className="student-app-shell">
    <aside className="student-sidebar">
      <NavLink to="/student/dashboard" className="student-brand"><span className="student-brand-mark"><BookOpenCheck size={19} /></span><span>Student Query<br /><b>Manager</b></span></NavLink>
      <div className="sidebar-section-label">WORKSPACE</div>
      <nav className="student-nav" aria-label="Student workspace">
        {navItems.map(({ to, label, icon: Icon, end }) => <NavLink key={to} to={to} end={end} className={({ isActive }) => `student-nav-link${isActive ? ' active' : ''}`}><Icon size={17} /><span>{label}</span></NavLink>)}
        <NavLink to="/student/queries/new" className={({ isActive }) => `student-nav-link${isActive ? ' active' : ''}`}><Plus size={17} /><span>Raise a query</span></NavLink>
        <NavLink to="/student/ask-ai" className={({ isActive }) => `student-nav-link${isActive ? ' active' : ''}`}><Sparkles size={17} /><span>Ask AI</span></NavLink>
      </nav>
      <div className="sidebar-spacer" />
      <div className="sidebar-help-card"><span className="help-card-icon"><CircleHelp size={16} /></span><strong>Need a hand?</strong><span>Your questions belong here.</span><ArrowUpRight size={15} className="help-card-arrow" /></div>
      <div className="sidebar-profile"><span className="profile-avatar">{user?.full_name.slice(0, 1).toUpperCase()}</span><span className="profile-copy"><strong>{user?.full_name}</strong><small>Student</small></span><button className="profile-logout" type="button" onClick={logout} aria-label="Sign out" title="Sign out"><LogOut size={16} /></button></div>
    </aside>
    <div className="student-main-column">
      <header className="student-mobile-header"><NavLink to="/student/dashboard" className="student-brand"><span className="student-brand-mark"><BookOpenCheck size={18} /></span><span>Student Query <b>Manager</b></span></NavLink><button className="profile-logout" type="button" onClick={logout} aria-label="Sign out"><LogOut size={16} /></button></header>
      <nav className="student-mobile-nav" aria-label="Student workspace">{navItems.map(({ to, label, icon: Icon, end }) => <NavLink key={to} to={to} end={end} className={({ isActive }) => `mobile-nav-link${isActive ? ' active' : ''}`}><Icon size={15} />{label}</NavLink>)}<NavLink to="/student/queries/new" className={({ isActive }) => `mobile-nav-link${isActive ? ' active' : ''}`}><Plus size={15} />New query</NavLink><NavLink to="/student/ask-ai" className={({ isActive }) => `mobile-nav-link${isActive ? ' active' : ''}`}><Sparkles size={15} />Ask AI</NavLink></nav>
      <main className="student-content"><Outlet /></main>
      <footer className="student-footer"><span>Student Query Manager</span><span>Academic support, thoughtfully connected</span></footer>
    </div>
  </div>
}
