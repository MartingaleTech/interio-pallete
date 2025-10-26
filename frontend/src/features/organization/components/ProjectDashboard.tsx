import { useState } from 'react'
import { useAuth } from '../../../state/AuthContext'
import { DashboardHeader } from '../../../components/shared/DashboardHeader'
import { Button } from '@/components/ui/button'
import { ArrowLeft, FileText, Users, Bell, Paperclip, LifeBuoy, MessageSquare, Calendar, FolderOpen } from 'lucide-react'
import { Project } from '../../../types'
import { ProjectProfile } from './project-dashboard/ProjectProfile'
import { ProjectTeam } from './project-dashboard/ProjectTeam'
import { ProjectInvoices } from './project-dashboard/ProjectInvoices'
import { ProjectNotifications } from './project-dashboard/ProjectNotifications'
import { ProjectAttachments } from './project-dashboard/ProjectAttachments'
import { ProjectSupport } from './project-dashboard/ProjectSupport'
import { ProjectDailyUpdates } from './project-dashboard/ProjectDailyUpdates'
import { ProjectCalendar } from './project-dashboard/ProjectCalendar'

interface ProjectDashboardProps {
  project: Project
  onBack: () => void
}

type ProjectView = 'profile' | 'team' | 'invoices' | 'notifications' | 'attachments' | 'support' | 'updates' | 'calendar'

export function ProjectDashboard({ project, onBack }: ProjectDashboardProps) {
  const { user, logout, token } = useAuth()
  const [activeView, setActiveView] = useState<ProjectView>('profile')
  const [unreadNotifications, setUnreadNotifications] = useState(0)

  if (!user || !token) return null

  const menuItems = [
    { id: 'profile' as ProjectView, label: 'Project Profile', icon: FolderOpen },
    { id: 'team' as ProjectView, label: 'Team', icon: Users },
    { id: 'invoices' as ProjectView, label: 'Invoices', icon: FileText },
    { id: 'notifications' as ProjectView, label: 'Notifications', icon: Bell, badge: unreadNotifications },
    { id: 'attachments' as ProjectView, label: 'Attachments & Designs', icon: Paperclip },
    { id: 'support' as ProjectView, label: 'Support', icon: LifeBuoy },
    { id: 'updates' as ProjectView, label: 'Daily Updates', icon: MessageSquare },
    { id: 'calendar' as ProjectView, label: 'Calendar', icon: Calendar },
  ]

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col lg:flex-row">
      {/* Sidebar - Mobile: Hidden by default, Desktop: Always visible */}
      <aside className="w-full lg:w-64 bg-white border-b lg:border-r lg:border-b-0 shadow-sm">
        <div className="p-4 border-b">
          <Button variant="ghost" onClick={onBack} className="mb-2 w-full justify-start">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Projects
          </Button>
          <h2 className="text-lg font-semibold truncate">{project.name}</h2>
          <p className="text-sm text-gray-500 truncate">{project.client_name}</p>
        </div>
        
        <nav className="p-2">
          <div className="grid grid-cols-2 lg:grid-cols-1 gap-1">
            {menuItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveView(item.id)}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                  activeView === item.id
                    ? 'bg-blue-50 text-blue-600 font-medium'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <item.icon className="w-4 h-4 flex-shrink-0" />
                <span className="truncate">{item.label}</span>
                {item.badge !== undefined && item.badge > 0 && (
                  <span className="ml-auto bg-red-500 text-white text-xs rounded-full px-2 py-0.5 min-w-[20px] text-center">
                    {item.badge}
                  </span>
                )}
              </button>
            ))}
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        <DashboardHeader 
          title={`Project: ${project.name}`}
          userName={user.name} 
          onLogout={logout} 
        />

        <main className="flex-1 p-4 lg:p-8 overflow-auto">
          {activeView === 'profile' && <ProjectProfile project={project} token={token} />}
          {activeView === 'team' && <ProjectTeam project={project} token={token} />}
          {activeView === 'invoices' && <ProjectInvoices project={project} token={token} />}
          {activeView === 'notifications' && (
            <ProjectNotifications 
              project={project} 
              token={token} 
              onUnreadCountChange={setUnreadNotifications}
            />
          )}
          {activeView === 'attachments' && <ProjectAttachments project={project} token={token} />}
          {activeView === 'support' && <ProjectSupport project={project} token={token} />}
          {activeView === 'updates' && <ProjectDailyUpdates project={project} token={token} />}
          {activeView === 'calendar' && <ProjectCalendar project={project} token={token} />}
        </main>
      </div>
    </div>
  )
}
