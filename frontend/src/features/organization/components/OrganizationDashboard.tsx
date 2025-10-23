import { useState, useEffect } from 'react'
import { Home, Users, Calendar, FileText, UserPlus, LifeBuoy } from 'lucide-react'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
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

export function OrganizationDashboard() {
  const { user, logout, token } = useAuth()
  const [activeTab, setActiveTab] = useState('projects')
  const [projects, setProjects] = useState<Project[]>([])
  const [clients, setClients] = useState<Client[]>([])
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([])

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

  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardHeader 
        title="Organization Dashboard" 
        userName={user.name} 
        onLogout={logout} 
      />

      <main className="max-w-7xl mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full max-w-3xl grid-cols-6">
            <TabsTrigger value="projects">
              <Home className="w-4 h-4 mr-2" />
              Projects
            </TabsTrigger>
            <TabsTrigger value="clients">
              <Users className="w-4 h-4 mr-2" />
              Clients
            </TabsTrigger>
            <TabsTrigger value="team">
              <UserPlus className="w-4 h-4 mr-2" />
              Team
            </TabsTrigger>
            <TabsTrigger value="tickets">
              <LifeBuoy className="w-4 h-4 mr-2" />
              Tickets
            </TabsTrigger>
            <TabsTrigger value="calendar">
              <Calendar className="w-4 h-4 mr-2" />
              Calendar
            </TabsTrigger>
            <TabsTrigger value="invoices">
              <FileText className="w-4 h-4 mr-2" />
              Invoices
            </TabsTrigger>
          </TabsList>

          <ProjectsTab 
            projects={projects} 
            clients={clients}
            onRefresh={fetchProjects}
          />
          
          <ClientsTab 
            clients={clients}
            onRefresh={fetchClients}
          />
          
          <TeamTab 
            teamMembers={teamMembers}
            onRefresh={fetchTeamMembers}
          />
          
          <TicketsTab 
            projects={projects}
          />
          
          <CalendarTab 
            projects={projects}
          />
          
          <InvoicesTab 
            projects={projects}
          />
        </Tabs>
      </main>
    </div>
  )
}
