import { useState } from 'react'
import { Plus, UserPlus, Upload } from 'lucide-react'
import { TabsContent } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { useAuth } from '../../../../state/AuthContext'
import { organizationService } from '../../../../services/organizationService'
import { Project, EventFormData, TeamMemberFormData, DesignFormData } from '../../../../types'

interface CalendarTabProps {
  projects: Project[]
}

export function CalendarTab({ projects }: CalendarTabProps) {
  const { token } = useAuth()
  const [showEventDialog, setShowEventDialog] = useState(false)
  const [showTeamDialog, setShowTeamDialog] = useState(false)
  const [showDesignDialog, setShowDesignDialog] = useState(false)
  
  const [eventFormData, setEventFormData] = useState<EventFormData>({
    project_id: '',
    title: '',
    description: '',
    event_date: '',
    event_time: ''
  })
  
  const [teamFormData, setTeamFormData] = useState<TeamMemberFormData>({
    project_id: '',
    name: '',
    email: '',
    phone: '',
    role: ''
  })
  
  const [designFormData, setDesignFormData] = useState<DesignFormData>({
    project_id: '',
    title: '',
    description: '',
    file: null
  })
  
  const [isLoading, setIsLoading] = useState(false)

  const handleCreateEvent = async () => {
    if (!token) return
    setIsLoading(true)
    try {
      await organizationService.createEvent(token, eventFormData)
      alert('Event created successfully!')
      setShowEventDialog(false)
      setEventFormData({ project_id: '', title: '', description: '', event_date: '', event_time: '' })
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to create event')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAddTeamMember = async () => {
    if (!token || !teamFormData.project_id) return
    setIsLoading(true)
    try {
      await organizationService.addProjectTeamMember(token, teamFormData.project_id, {
        name: teamFormData.name,
        email: teamFormData.email,
        phone: teamFormData.phone,
        role: teamFormData.role
      })
      alert('Team member added successfully!')
      setShowTeamDialog(false)
      setTeamFormData({ project_id: '', name: '', email: '', phone: '', role: '' })
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to add team member')
    } finally {
      setIsLoading(false)
    }
  }

  const handleUploadDesign = async () => {
    if (!token) return
    setIsLoading(true)
    try {
      await organizationService.uploadDesign(token, designFormData)
      alert('Design uploaded successfully!')
      setShowDesignDialog(false)
      setDesignFormData({ project_id: '', title: '', description: '', file: null })
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to upload design')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <TabsContent value="calendar" className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">Calendar & Team</h2>
        <div className="flex gap-2">
          <Dialog open={showTeamDialog} onOpenChange={setShowTeamDialog}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <UserPlus className="w-4 h-4 mr-2" />
                Add Team Member
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Add Team Member</DialogTitle>
                <DialogDescription>
                  Add a new team member to a project
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="team-project">Project</Label>
                  <Select 
                    value={teamFormData.project_id} 
                    onValueChange={(value) => setTeamFormData({ ...teamFormData, project_id: value })}
                  >
                    <SelectTrigger id="team-project">
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
                  <Label htmlFor="team-name">Name</Label>
                  <Input
                    id="team-name"
                    placeholder="Team member name"
                    value={teamFormData.name}
                    onChange={(e) => setTeamFormData({ ...teamFormData, name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="team-email">Email</Label>
                  <Input
                    id="team-email"
                    type="email"
                    placeholder="team@example.com"
                    value={teamFormData.email}
                    onChange={(e) => setTeamFormData({ ...teamFormData, email: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="team-phone">Phone</Label>
                  <Input
                    id="team-phone"
                    type="tel"
                    placeholder="Phone number"
                    value={teamFormData.phone}
                    onChange={(e) => setTeamFormData({ ...teamFormData, phone: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="team-role">Role</Label>
                  <Input
                    id="team-role"
                    placeholder="e.g., Designer, Contractor"
                    value={teamFormData.role}
                    onChange={(e) => setTeamFormData({ ...teamFormData, role: e.target.value })}
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <Button onClick={handleAddTeamMember} className="flex-1" disabled={isLoading}>
                  {isLoading ? 'Adding...' : 'Add Member'}
                </Button>
                <Button onClick={() => setShowTeamDialog(false)} variant="outline" className="flex-1">
                  Cancel
                </Button>
              </div>
            </DialogContent>
          </Dialog>

          <Dialog open={showEventDialog} onOpenChange={setShowEventDialog}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Add Event
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Add Calendar Event</DialogTitle>
                <DialogDescription>
                  Schedule a new event for a project
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="event-project">Project</Label>
                  <Select 
                    value={eventFormData.project_id} 
                    onValueChange={(value) => setEventFormData({ ...eventFormData, project_id: value })}
                  >
                    <SelectTrigger id="event-project">
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
                  <Label htmlFor="event-title">Event Title</Label>
                  <Input
                    id="event-title"
                    placeholder="Event title"
                    value={eventFormData.title}
                    onChange={(e) => setEventFormData({ ...eventFormData, title: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="event-description">Description</Label>
                  <Textarea
                    id="event-description"
                    placeholder="Event description"
                    value={eventFormData.description}
                    onChange={(e) => setEventFormData({ ...eventFormData, description: e.target.value })}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="event-date">Date</Label>
                    <Input
                      id="event-date"
                      type="date"
                      value={eventFormData.event_date}
                      onChange={(e) => setEventFormData({ ...eventFormData, event_date: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="event-time">Time</Label>
                    <Input
                      id="event-time"
                      type="time"
                      value={eventFormData.event_time}
                      onChange={(e) => setEventFormData({ ...eventFormData, event_time: e.target.value })}
                    />
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                <Button onClick={handleCreateEvent} className="flex-1" disabled={isLoading}>
                  {isLoading ? 'Creating...' : 'Create Event'}
                </Button>
                <Button onClick={() => setShowEventDialog(false)} variant="outline" className="flex-1">
                  Cancel
                </Button>
              </div>
            </DialogContent>
          </Dialog>

          <Dialog open={showDesignDialog} onOpenChange={setShowDesignDialog}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Upload className="w-4 h-4 mr-2" />
                Upload Design
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Upload Design</DialogTitle>
                <DialogDescription>
                  Upload a design file for a project
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="design-project">Project</Label>
                  <Select 
                    value={designFormData.project_id} 
                    onValueChange={(value) => setDesignFormData({ ...designFormData, project_id: value })}
                  >
                    <SelectTrigger id="design-project">
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
                  <Label htmlFor="design-title">Title</Label>
                  <Input
                    id="design-title"
                    placeholder="Design title"
                    value={designFormData.title}
                    onChange={(e) => setDesignFormData({ ...designFormData, title: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="design-description">Description</Label>
                  <Textarea
                    id="design-description"
                    placeholder="Design description"
                    value={designFormData.description}
                    onChange={(e) => setDesignFormData({ ...designFormData, description: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="design-file">File</Label>
                  <Input
                    id="design-file"
                    type="file"
                    onChange={(e) => setDesignFormData({ ...designFormData, file: e.target.files?.[0] || null })}
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <Button onClick={handleUploadDesign} className="flex-1" disabled={isLoading}>
                  {isLoading ? 'Uploading...' : 'Upload'}
                </Button>
                <Button onClick={() => setShowDesignDialog(false)} variant="outline" className="flex-1">
                  Cancel
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>
      <p className="text-gray-500">Calendar functionality coming soon...</p>
    </TabsContent>
  )
}
