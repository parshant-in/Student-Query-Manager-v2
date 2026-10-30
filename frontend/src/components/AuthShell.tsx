import { ArrowUpRight, BookOpen, Sparkles } from 'lucide-react'
import type { PropsWithChildren } from 'react'
import { Link } from 'react-router-dom'
import { Brand } from './Brand'

export function AuthShell({ children, mode }: PropsWithChildren<{ mode: 'login' | 'register' }>) {
  return <main className="auth-page">
    <section className="auth-form-panel">
      <header className="auth-topbar"><Brand /><span className="topbar-note">A calmer way to find clarity</span></header>
      <div className="auth-form-wrap">
        <div className="mobile-mark"><Brand /></div>
        {children}
        <p className="auth-switch">
          {mode === 'login' ? 'New to Student Query Manager?' : 'Already have an account?'}{' '}
          <Link to={mode === 'login' ? '/register' : '/login'}>{mode === 'login' ? 'Create an account' : 'Sign in'}</Link>
        </p>
      </div>
      <footer className="auth-footer"><span>© 2026 Student Query Manager</span><span>Academic support, thoughtfully connected</span></footer>
    </section>
    <aside className="auth-story-panel">
      <div className="story-orbit orbit-one" /><div className="story-orbit orbit-two" />
      <div className="story-content">
        <span className="story-eyebrow"><Sparkles size={14} /> YOUR ACADEMIC COMPANION</span>
        <h2>Good questions<br />deserve <em>clear answers.</em></h2>
        <p>A thoughtful space to connect with faculty, find guidance, and keep your academic journey moving.</p>
        <div className="story-note"><span className="note-icon"><BookOpen size={18} /></span><div><strong>Every conversation, in one place</strong><span>Support that stays with you.</span></div><ArrowUpRight size={17} className="note-arrow" /></div>
      </div>
      <div className="story-caption"><span>LEARN WITH CONFIDENCE</span><span>01 — 03</span></div>
    </aside>
  </main>
}
