import { Navigate, Route, Routes } from 'react-router-dom'
import { GuestOnly, RequireAuth } from './components/RouteGuards'
import { useAuth } from './context/AuthContext'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { StudentLayout } from './components/StudentLayout'
import { NewQueryPage } from './pages/NewQueryPage'
import { QueryDetailPage } from './pages/QueryDetailPage'
import { StudentDashboardPage } from './pages/StudentDashboardPage'
import { StudentQueriesPage } from './pages/StudentQueriesPage'
import { FacultyLayout } from './components/FacultyLayout'
import { FacultyDashboardPage } from './pages/FacultyDashboardPage'
import { FacultyQueriesPage } from './pages/FacultyQueriesPage'
import { FacultyQueryDetailPage } from './pages/FacultyQueryDetailPage'
import { KnowledgeBasePage } from './pages/KnowledgeBasePage'
import { AdminKnowledgeBasePage } from './pages/AdminKnowledgeBasePage'
import { AdminDashboardPage } from './pages/AdminDashboardPage'
import { AskAIPage } from './pages/AskAIPage'
import { dashboardPath } from './lib/routes'

function HomeRedirect() {
  const { user } = useAuth()
  return <Navigate to={user ? dashboardPath(user.role) : '/login'} replace />
}

export default function App() {
  return <Routes>
    <Route path="/" element={<HomeRedirect />} />
    <Route path="/login" element={<GuestOnly><LoginPage /></GuestOnly>} />
    <Route path="/register" element={<GuestOnly><RegisterPage /></GuestOnly>} />
    <Route element={<RequireAuth roles={['student']} />}>
      <Route element={<StudentLayout />}>
        <Route path="/student/dashboard" element={<StudentDashboardPage />} />
        <Route path="/student/queries" element={<StudentQueriesPage />} />
        <Route path="/student/queries/new" element={<NewQueryPage />} />
        <Route path="/student/queries/:queryId" element={<QueryDetailPage />} />
        <Route path="/student/ask-ai" element={<AskAIPage />} />
      </Route>
    </Route>
    <Route element={<RequireAuth roles={['faculty']} />}>
      <Route element={<FacultyLayout />}>
        <Route path="/faculty/dashboard" element={<FacultyDashboardPage />} />
        <Route path="/faculty/queries" element={<FacultyQueriesPage />} />
        <Route path="/faculty/queries/:queryId" element={<FacultyQueryDetailPage />} />
        <Route path="/faculty/knowledge-base" element={<KnowledgeBasePage />} />
      </Route>
    </Route>
    <Route element={<RequireAuth roles={['admin']} />}>
      <Route path="/admin/dashboard" element={<AdminDashboardPage />} />
      <Route path="/admin/knowledge-base" element={<AdminKnowledgeBasePage />} />
    </Route>
    <Route path="*" element={<HomeRedirect />} />
  </Routes>
}
