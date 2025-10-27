import { useState, useEffect } from 'react'
import { Home, Users, Calendar, FileText, UserPlus, LifeBuoy, MessageSquare } from 'lucide-react'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { DashboardHeader } from '../../../components/shared/DashboardHeader'
import { useAuth } from '../../../state/AuthContext'
import { organizationService } from '../../../services/organizationService'
import { Project, Client, TeamMember } from '../../../types'
import { ProjectsTab } from './tabs/ProjectsTab'
import { ClientsTab } from './tabs/ClientsTab'
import { TeamTab } from './tabs/TeamTab'
import { CalendarTab } from './tabs/CalendarTab'
import { InvoicesTab } from './tabs/InvoicesTab'
import { TicketsTab } from './tabs/TicketsTab'
import { ProjectDashboard } from './ProjectDashboard'
import { Chat } from '../../chat/components/Chat'

export function OrganizationDashboard() {
  const { user, logout, token } = useAuth()
  const [activeTab, setActiveTab] = useState('projects')
  const [projects, setProjects] = useState<Project[]>([])
  const [clients, setClients] = useState<Client[]>([])
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([])
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)

  useEffect(() => {
    if (token) {
      fetchProjects()
      fetchClients()
      fetchTeamMembers()
    }
  }, [token])

  const fetchProjects = async () => {
    if (!token) return
    try {
      const data = await organizationService.getProjects(token)
      setProjects(data)
    } catch (error) {
      console.error('Failed to fetch projects', error)
    }
  }

  const fetchClients = async () => {
    if (!token) return
    try {
      const data = await organizationService.getClients(token)
      setClients(data)
    } catch (error) {
      console.error('Failed to fetch clients', error)
    }
  }

  const fetchTeamMembers = async () => {
    if (!token) return
    try {
      const data = await organizationService.getTeamMembers(token)
      setTeamMembers(data)
    } catch (error) {
      console.error('Failed to fetch team members', error)
    }
  }

  if (!user) return null

  if (selectedProject) {
    return (
      <ProjectDashboard 
        project={selectedProject} 
        onBack={() => setSelectedProject(null)}
      />
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardHeader 
        title="Organization Dashboard" 
        userName={user.name} 
        onLogout={logout} 
      />

      <main className="max-w-7xl mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full max-w-4xl grid-cols-7 gap-1">
            <TabsTrigger value="projects" className="text-xs sm:text-sm">
              <Home className="w-4 h-4 sm:mr-2" />
              <span className="hidden sm:inline">Projects</span>
            </TabsTrigger>
            <TabsTrigger value="clients" className="text-xs sm:text-sm">
              <Users className="w-4 h-4 sm:mr-2" />
              <span className="hidden sm:inline">Clients</span>
            </TabsTrigger>
            <TabsTrigger value="team" className="text-xs sm:text-sm">
              <UserPlus className="w-4 h-4 sm:mr-2" />
              <span className="hidden sm:inline">Team</span>
            </TabsTrigger>
            <TabsTrigger value="chat" className="text-xs sm:text-sm">
              <MessageSquare className="w-4 h-4 sm:mr-2" />
              <span className="hidden sm:inline">Chat</span>
            </TabsTrigger>
            <TabsTrigger value="tickets" className="text-xs sm:text-sm">
              <LifeBuoy className="w-4 h-4 sm:mr-2" />
              <span className="hidden sm:inline">Tickets</span>
            </TabsTrigger>
            <TabsTrigger value="calendar" className="text-xs sm:text-sm">
              <Calendar className="w-4 h-4 sm:mr-2" />
              <span className="hidden sm:inline">Calendar</span>
            </TabsTrigger>
            <TabsTrigger value="invoices" className="text-xs sm:text-sm">
              <FileText className="w-4 h-4 sm:mr-2" />
              <span className="hidden sm:inline">Invoices</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="projects">
            <ProjectsTab 
              projects={projects} 
              clients={clients}
              onRefresh={fetchProjects}
              onViewProject={setSelectedProject}
            />
          </TabsContent>
          
          <TabsContent value="clients">
            <ClientsTab 
              clients={clients}
              onRefresh={fetchClients}
            />
          </TabsContent>
          
          <TabsContent value="team">
            <TeamTab 
              teamMembers={teamMembers}
              onRefresh={fetchTeamMembers}
            />
          </TabsContent>
          
          <TabsContent value="chat">
            <div className="h-[calc(100vh-250px)]">
              <Chat />
            </div>
          </TabsContent>
          
          <TabsContent value="tickets">
            <TicketsTab 
              projects={projects}
            />
          </TabsContent>
          
          <TabsContent value="calendar">
            <CalendarTab 
              projects={projects}
            />
          </TabsContent>
          
          <TabsContent value="invoices">
            <InvoicesTab 
              projects={projects}
            />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
