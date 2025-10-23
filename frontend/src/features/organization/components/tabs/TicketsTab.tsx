import { useState, useEffect } from 'react'
import { Plus, AlertCircle, CheckCircle, Clock, XCircle } from 'lucide-react'
import { TabsContent } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '../../../../state/AuthContext'
import { ticketService } from '../../../../services/ticketService'
import { Project, ProjectTicket, ProjectTicketFormData, TicketStatus, TicketPriority, TicketType } from '../../../../types'

interface TicketsTabProps {
  projects: Project[]
}

const ticketTypeLabels: Record<TicketType, string> = {
  project_issue: 'Project Issue',
  design_change: 'Design Change',
  correction: 'Correction',
  missing_item: 'Missing Item',
  interior_work: 'Interior Work',
  app_issue: 'App Issue',
  invoice_issue: 'Invoice Issue',
  access_issue: 'Access Issue',
  plan_issue: 'Plan Issue',
  other: 'Other'
}

const priorityColors: Record<TicketPriority, string> = {
  low: 'bg-gray-500',
  medium: 'bg-blue-500',
  high: 'bg-orange-500',
  urgent: 'bg-red-500'
}

const statusIcons: Record<TicketStatus, any> = {
  open: AlertCircle,
  in_progress: Clock,
  resolved: CheckCircle,
  closed: CheckCircle,
  reopened: AlertCircle
}

export function TicketsTab({ projects }: TicketsTabProps) {
  const { token } = useAuth()
  const [tickets, setTickets] = useState<ProjectTicket[]>([])
  const [showDialog, setShowDialog] = useState(false)
  const [selectedProject, setSelectedProject] = useState<string>('')
  const [formData, setFormData] = useState<ProjectTicketFormData>({
    title: '',
    description: '',
    ticket_type: 'project_issue',
    priority: 'medium'
  })
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (token && projects.length > 0) {
      fetchAllTickets()
    }
  }, [token, projects])

  const fetchAllTickets = async () => {
    if (!token) return
    try {
      const allTickets: ProjectTicket[] = []
      for (const project of projects) {
        const projectTickets = await ticketService.getProjectTickets(token, project.id)
        allTickets.push(...projectTickets)
      }
      setTickets(allTickets)
    } catch (error) {
      console.error('Failed to fetch tickets', error)
    }
  }

  const handleSubmit = async () => {
    if (!token || !selectedProject) return
    setIsLoading(true)
    try {
      await ticketService.createProjectTicket(token, selectedProject, formData)
      alert('Ticket created successfully!')
      setShowDialog(false)
      setFormData({ title: '', description: '', ticket_type: 'project_issue', priority: 'medium' })
      setSelectedProject('')
      fetchAllTickets()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to create ticket')
    } finally {
      setIsLoading(false)
    }
  }

  const getProjectName = (projectId: string) => {
    const project = projects.find(p => p.id === projectId)
    return project?.name || 'Unknown Project'
  }

  const StatusIcon = ({ status }: { status: TicketStatus }) => {
    const Icon = statusIcons[status]
    return <Icon className="w-4 h-4" />
  }

  return (
    <TabsContent value="tickets" className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Support Tickets</h2>
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              New Ticket
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>Create Support Ticket</DialogTitle>
              <DialogDescription>Report an issue or request a change</DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="ticket-project">Project</Label>
                <Select 
                  value={selectedProject} 
                  onValueChange={setSelectedProject}
                >
                  <SelectTrigger id="ticket-project">
                    <SelectValue placeholder="Select a project" />
                  </SelectTrigger>
                  <SelectContent>
                    {projects.map((project) => (
                      <SelectItem key={project.id} value={project.id}>
                        {project.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="ticket-title">Title</Label>
                <Input
                  id="ticket-title"
                  placeholder="Brief description of the issue"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="ticket-type">Type</Label>
                <Select 
                  value={formData.ticket_type} 
                  onValueChange={(value) => setFormData({ ...formData, ticket_type: value as TicketType })}
                >
                  <SelectTrigger id="ticket-type">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(ticketTypeLabels).map(([value, label]) => (
                      <SelectItem key={value} value={value}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="ticket-priority">Priority</Label>
                <Select 
                  value={formData.priority} 
                  onValueChange={(value) => setFormData({ ...formData, priority: value as TicketPriority })}
                >
                  <SelectTrigger id="ticket-priority">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="urgent">Urgent</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="ticket-description">Description</Label>
                <Textarea
                  id="ticket-description"
                  placeholder="Detailed description of the issue"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={4}
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSubmit} className="flex-1" disabled={isLoading || !selectedProject}>
                {isLoading ? 'Creating...' : 'Create Ticket'}
              </Button>
              <Button onClick={() => setShowDialog(false)} variant="outline" className="flex-1">
                Cancel
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {tickets.map((ticket) => (
          <Card key={ticket.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-lg">{ticket.title}</CardTitle>
                  <CardDescription className="mt-1">{getProjectName(ticket.project_id)}</CardDescription>
                </div>
                <Badge className={priorityColors[ticket.priority]}>
                  {ticket.priority}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <StatusIcon status={ticket.status} />
                <span className="font-medium capitalize">{ticket.status.replace('_', ' ')}</span>
              </div>
              <div className="text-sm">
                <span className="font-medium">Type:</span> {ticketTypeLabels[ticket.ticket_type]}
              </div>
              <div className="text-sm text-gray-600 line-clamp-2">
                {ticket.description}
              </div>
              {ticket.assignee_name && (
                <div className="text-sm">
                  <span className="font-medium">Assigned to:</span> {ticket.assignee_name}
                </div>
              )}
              <div className="text-xs text-gray-500">
                Created {new Date(ticket.created_at).toLocaleDateString()}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      {tickets.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            No tickets yet. Create a ticket to report issues or request changes.
          </CardContent>
        </Card>
      )}
    </TabsContent>
  )
}
