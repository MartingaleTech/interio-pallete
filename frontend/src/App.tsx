import { AuthProvider, useAuth } from './state/AuthContext'
import { LoginForm } from './features/auth/components/LoginForm'
import { AdminDashboard } from './features/admin/components/AdminDashboard'
import { OrganizationDashboard } from './features/organization/components/OrganizationDashboard'
import { ClientDashboard } from './features/client/components/ClientDashboard'
import './App.css'

function AppContent() {
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
    return <LoginForm />
  }

  if (user.role === 'admin') {
    return <AdminDashboard />
  } else if (user.role === 'org_owner' || user.role === 'org_member') {
    return <OrganizationDashboard />
  } else if (user.role === 'client') {
    return <ClientDashboard />
  }

  return null
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
