import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { DashboardHeader } from '../../../components/shared/DashboardHeader'
import { useAuth } from '../../../state/AuthContext'
import { clientService } from '../../../services/clientService'
import { Project } from '../../../types'

export function ClientDashboard() {
  const { user, logout, token } = useAuth()
  const [projects, setProjects] = useState<Project[]>([])

  useEffect(() => {
    if (token) {
      fetchProjects()
    }
  }, [token])

  const fetchProjects = async () => {
    if (!token) return
    try {
      const data = await clientService.getProjects(token)
      setProjects(data)
    } catch (error) {
      console.error('Failed to fetch projects', error)
    }
  }

  if (!user) return null

  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardHeader 
        title="Client Dashboard" 
        userName={user.name} 
        onLogout={logout} 
      />

      <main className="max-w-7xl mx-auto px-4 py-8">
        <h2 className="text-2xl font-bold mb-6">My Projects</h2>
        
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <Card key={project.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-lg">{project.name}</CardTitle>
                <CardDescription>{project.description}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="text-sm">
                  <span className="font-medium">Budget:</span> ₹{project.budget.toLocaleString()}
                </div>
                <div className="text-sm">
                  <span className="font-medium">Status:</span> {project.status}
                </div>
                <div className="text-sm">
                  <span className="font-medium">Start Date:</span> {new Date(project.start_date).toLocaleDateString()}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {projects.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center text-gray-500">
              No projects assigned yet. Please contact your designer for project details.
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  )
}
