import { useState, useEffect } from 'react'
import { DashboardHeader } from '../../../components/shared/DashboardHeader'
import { useAuth } from '../../../state/AuthContext'
import { adminService } from '../../../services/adminService'
import { AdminSidebar } from './AdminSidebar'
import { AdminOverview } from './AdminOverview'
import { AdminOrganizationsList } from './AdminOrganizationsList'
import { AdminTickets } from './AdminTickets'
import { AdminNotifications } from './AdminNotifications'
import { AdminAnalytics } from './AdminAnalytics'
import { OrgDashboard } from './OrgDashboard'

export function AdminDashboard() {
  const { user, logout, token } = useAuth()
  const [activeView, setActiveView] = useState<string>('overview')
  const [selectedOrgId, setSelectedOrgId] = useState<string | null>(null)
  const [unreadNotifications, setUnreadNotifications] = useState(0)

  useEffect(() => {
    if (token) {
      fetchUnreadNotifications()
    }
  }, [token])

  const fetchUnreadNotifications = async () => {
    if (!token) return
    try {
      const notifications = await adminService.getNotifications(token, true)
      setUnreadNotifications(notifications.length)
    } catch (error) {
      console.error('Failed to fetch notifications', error)
    }
  }

  const handleSelectOrg = (orgId: string) => {
    setSelectedOrgId(orgId)
    setActiveView('org-detail')
  }

  const handleBackFromOrg = () => {
    setSelectedOrgId(null)
    setActiveView('organizations')
  }

  if (!user || !token) return null

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <AdminSidebar 
        activeView={activeView} 
        onViewChange={setActiveView}
        unreadNotifications={unreadNotifications}
      />
      
      <div className="flex-1 flex flex-col">
        <DashboardHeader 
          title="Admin Dashboard" 
          userName={user.name} 
          onLogout={logout} 
        />

        <main className="flex-1">
          {activeView === 'overview' && (
            <AdminOverview token={token} onSelectOrg={handleSelectOrg} />
          )}
          
          {activeView === 'organizations' && (
            <AdminOrganizationsList token={token} onSelectOrg={handleSelectOrg} />
          )}
          
          {activeView === 'tickets' && (
            <AdminTickets token={token} />
          )}
          
          {activeView === 'notifications' && (
            <AdminNotifications token={token} />
          )}
          
          {activeView === 'analytics' && (
            <AdminAnalytics />
          )}
          
          {activeView === 'org-detail' && selectedOrgId && (
            <OrgDashboard 
              orgId={selectedOrgId} 
              token={token} 
              onBack={handleBackFromOrg}
            />
          )}
        </main>
      </div>
    </div>
  )
}
