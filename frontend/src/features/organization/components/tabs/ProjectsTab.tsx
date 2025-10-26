import { useState } from 'react'
import { Plus } from 'lucide-react'
import { TabsContent } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { useAuth } from '../../../../state/AuthContext'
import { organizationService } from '../../../../services/organizationService'
import { Project, Client, ProjectFormData } from '../../../../types'

interface ProjectsTabProps {
  projects: Project[]
  clients: Client[]
  onRefresh: () => void
  onViewProject?: (project: Project) => void
}

export function ProjectsTab({ projects, clients, onRefresh, onViewProject }: ProjectsTabProps) {
  const { token } = useAuth()
  const [showDialog, setShowDialog] = useState(false)
  const [formData, setFormData] = useState<ProjectFormData>({
    client_id: '',
    name: '',
    description: '',
    budget: '',
    start_date: '',
    end_date: ''
  })
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async () => {
    if (!token) return
    setIsLoading(true)
    try {
      await organizationService.createProject(token, formData)
      alert('Project created successfully!')
      setShowDialog(false)
      setFormData({ client_id: '', name: '', description: '', budget: '', start_date: '', end_date: '' })
      onRefresh()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to create project')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <TabsContent value="projects" className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Projects</h2>
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              New Project
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>Create New Project</DialogTitle>
              <DialogDescription>Add a new project for your client</DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="project-client">Client</Label>
                <Select 
                  value={formData.client_id} 
                  onValueChange={(value) => setFormData({ ...formData, client_id: value })}
                >
                  <SelectTrigger id="project-client">
                    <SelectValue placeholder="Select a client" />
                  </SelectTrigger>
                  <SelectContent>
                    {clients.map((client) => (
                      <SelectItem key={client.id} value={client.id}>
                        {client.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="project-name">Project Name</Label>
                <Input
                  id="project-name"
                  placeholder="Project name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="project-description">Description</Label>
                <Textarea
                  id="project-description"
                  placeholder="Project description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="project-budget">Budget (₹)</Label>
                <Input
                  id="project-budget"
                  type="number"
                  placeholder="100000"
                  value={formData.budget}
                  onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="project-start">Start Date</Label>
                  <Input
                    id="project-start"
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="project-end">End Date</Label>
                  <Input
                    id="project-end"
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                  />
                </div>
              </div>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSubmit} className="flex-1" disabled={isLoading}>
                {isLoading ? 'Creating...' : 'Create Project'}
              </Button>
              <Button onClick={() => setShowDialog(false)} variant="outline" className="flex-1">
                Cancel
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {projects.map((project) => (
          <Card key={project.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="text-lg">{project.name}</CardTitle>
              <CardDescription>{project.client_name}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="text-sm">
                <span className="font-medium">Budget:</span> ₹{project.budget.toLocaleString()}
              </div>
              <div className="text-sm">
                <span className="font-medium">Status:</span> {project.status}
              </div>
              <div className="text-sm">
                <span className="font-medium">Start:</span> {new Date(project.start_date).toLocaleDateString()}
              </div>
              {onViewProject && (
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full mt-2"
                  onClick={() => onViewProject(project)}
                >
                  View Project
                </Button>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
      {projects.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            No projects yet. Create clients first, then add projects.
          </CardContent>
        </Card>
      )}
    </TabsContent>
  )
}
