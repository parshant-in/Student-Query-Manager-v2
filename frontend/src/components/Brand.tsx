import { BookOpenCheck } from 'lucide-react'

export function Brand({ compact = false }: { compact?: boolean }) {
  return <div className="brand-lockup">
    <span className="brand-mark" aria-hidden="true"><BookOpenCheck size={20} strokeWidth={1.8} /></span>
    {!compact && <span className="brand-name">Student Query <span>Manager</span></span>}
  </div>
}
