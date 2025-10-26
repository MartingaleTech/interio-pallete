import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Plus, LifeBuoy } from 'lucide-react'
import { Project, ProjectTicket } from '../../../../types'
import { projectService } from '../../../../services/projectService'

interface ProjectSupportProps {
  project: Project
  token: string
}

export function ProjectSupport({ project, token }: ProjectSupportProps) {
  const [tickets, setTickets] = useState<ProjectTicket[]>([])
  const [showDialog, setShowDialog] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    ticket_type: 'project_issue',
    priority: 'medium'
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchTickets()
  }, [])

  const fetchTickets = async () => {
    try {
      const data = await projectService.getProjectTickets(token, project.id)
      setTickets(data)
    } catch (error) {
      console.error('Failed to fetch tickets', error)
    }
  }

  const handleSubmit = async () => {
    if (!formData.title || !formData.description) {
      alert('Please fill all required fields')
      return
    }

    setLoading(true)
    try {
      await projectService.createProjectTicket(token, project.id, formData)
      alert('Support ticket created successfully!')
      setShowDialog(false)
      setFormData({ title: '', description: '', ticket_type: 'project_issue', priority: 'medium' })
      fetchTickets()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to create ticket')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold mb-2">Support Tickets</h2>
          <p className="text-gray-600">Track issues and support requests for this project</p>
        </div>
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Create Ticket
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Create Support Ticket</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  placeholder="Brief description of the issue"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Detailed description of the issue"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={4}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="ticket_type">Type</Label>
                <Select value={formData.ticket_type} onValueChange={(value) => setFormData({ ...formData, ticket_type: value })}>
                  <SelectTrigger id="ticket_type">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="project_issue">Project Issue</SelectItem>
                    <SelectItem value="design_change">Design Change</SelectItem>
                    <SelectItem value="correction">Correction</SelectItem>
                    <SelectItem value="missing_item">Missing Item</SelectItem>
                    <SelectItem value="interior_work">Interior Work</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="priority">Priority</Label>
                <Select value={formData.priority} onValueChange={(value) => setFormData({ ...formData, priority: value })}>
                  <SelectTrigger id="priority">
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
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSubmit} className="flex-1" disabled={loading}>
                {loading ? 'Creating...' : 'Create Ticket'}
              </Button>
              <Button onClick={() => setShowDialog(false)} variant="outline" className="flex-1">
                Cancel
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-4">
        {tickets.map((ticket) => (
          <Card key={ticket.id}>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <LifeBuoy className="w-5 h-5" />
                {ticket.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <p className="text-gray-700">{ticket.description}</p>
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  <div>
                    <p className="text-sm text-gray-500">Type</p>
                    <p className="font-medium capitalize">{ticket.ticket_type.replace('_', ' ')}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Priority</p>
                    <span className={`inline-block px-3 py-1 rounded text-sm font-medium ${
                      ticket.priority === 'urgent'
                        ? 'bg-red-100 text-red-700'
                        : ticket.priority === 'high'
                        ? 'bg-orange-100 text-orange-700'
                        : ticket.priority === 'medium'
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-blue-100 text-blue-700'
                    }`}>
                      {ticket.priority}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Status</p>
                    <span className={`inline-block px-3 py-1 rounded text-sm font-medium ${
                      ticket.status === 'open'
                        ? 'bg-green-100 text-green-700'
                        : ticket.status === 'in_progress'
                        ? 'bg-blue-100 text-blue-700'
                        : ticket.status === 'resolved'
                        ? 'bg-gray-100 text-gray-700'
                        : 'bg-purple-100 text-purple-700'
                    }`}>
                      {ticket.status.replace('_', ' ')}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Created</p>
                    <p className="font-medium">{new Date(ticket.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
                {ticket.creator_name && (
                  <div className="pt-2 border-t">
                    <p className="text-xs text-gray-500">Created by {ticket.creator_name}</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {tickets.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            No support tickets yet. Create a ticket to report issues or request support.
          </CardContent>
        </Card>
      )}
    </div>
  )
}
