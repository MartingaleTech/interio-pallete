import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './state/AuthContext'
import { ChatProvider } from './state/ChatContext'
import { LoginForm } from './features/auth/components/LoginForm'
import { AdminDashboard } from './features/admin/components/AdminDashboard'
import { OrganizationDashboard } from './features/organization/components/OrganizationDashboard'
import { ClientDashboard } from './features/client/components/ClientDashboard'
import { LandingPage } from './pages/landing/LandingPage'
import { About } from './pages/About'
import { Contact } from './pages/Contact'
import { Support } from './pages/Support'
import './App.css'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-gray-500">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function DashboardRouter() {
  const { user } = useAuth()

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (user.role === 'admin') {
    return <AdminDashboard />
  } else if (user.role === 'org_owner' || user.role === 'org_member') {
    return <OrganizationDashboard />
  } else if (user.role === 'client') {
    return <ClientDashboard />
  }

  return <Navigate to="/login" replace />
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ChatProvider>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/about" element={<About />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/support" element={<Support />} />
            <Route path="/login" element={<LoginForm />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardRouter />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </ChatProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
