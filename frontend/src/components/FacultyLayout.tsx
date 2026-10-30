import { ArrowUpRight, BookOpenCheck, CircleHelp, Database, LayoutDashboard, LogOut } from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const navItems = [
  { to: '/faculty/dashboard', label: 'Overview', icon: LayoutDashboard, end: true },
  { to: '/faculty/queries', label: 'Department queries', icon: CircleHelp, end: false },
  { to: '/faculty/knowledge-base', label: 'Knowledge base', icon: Database, end: false },
]

export function FacultyLayout() {
  const { user, logout } = useAuth()
  return <div className="student-app-shell faculty-app-shell">
    <aside className="student-sidebar">
      <NavLink to="/faculty/dashboard" className="student-brand"><span className="student-brand-mark"><BookOpenCheck size={19} /></span><span>Student Query<br /><b>Manager</b></span></NavLink>
      <div className="sidebar-section-label">FACULTY WORKSPACE</div>
      <nav className="student-nav" aria-label="Faculty workspace">{navItems.map(({ to, label, icon: Icon, end }) => <NavLink key={to} to={to} end={end} className={({ isActive }) => `student-nav-link${isActive ? ' active' : ''}`}><Icon size={17} /><span>{label}</span></NavLink>)}</nav>
      <div className="sidebar-spacer" />
      <div className="sidebar-help-card"><span className="help-card-icon"><CircleHelp size={16} /></span><strong>Faculty workspace</strong><span>Supporting students, one query at a time.</span><ArrowUpRight size={15} className="help-card-arrow" /></div>
      <div className="sidebar-profile"><span className="profile-avatar">{user?.full_name.slice(0, 1).toUpperCase()}</span><span className="profile-copy"><strong>{user?.full_name}</strong><small>Faculty</small></span><button className="profile-logout" type="button" onClick={logout} aria-label="Sign out" title="Sign out"><LogOut size={16} /></button></div>
    </aside>
    <div className="student-main-column">
      <header className="student-mobile-header"><NavLink to="/faculty/dashboard" className="student-brand"><span className="student-brand-mark"><BookOpenCheck size={18} /></span><span>Student Query <b>Manager</b></span></NavLink><button className="profile-logout" type="button" onClick={logout} aria-label="Sign out"><LogOut size={16} /></button></header>
      <nav className="student-mobile-nav" aria-label="Faculty workspace">{navItems.map(({ to, label, icon: Icon, end }) => <NavLink key={to} to={to} end={end} className={({ isActive }) => `mobile-nav-link${isActive ? ' active' : ''}`}><Icon size={15} />{label}</NavLink>)}</nav>
      <main className="student-content"><Outlet /></main>
      <footer className="student-footer"><span>Student Query Manager</span><span>Faculty workspace</span></footer>
    </div>
  </div>
}
