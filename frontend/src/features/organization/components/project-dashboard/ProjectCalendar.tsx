import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Plus, Calendar as CalendarIcon } from 'lucide-react'
import { Project } from '../../../../types'
import { projectService } from '../../../../services/projectService'

interface ProjectCalendarProps {
  project: Project
  token: string
}

export function ProjectCalendar({ project, token }: ProjectCalendarProps) {
  const [events, setEvents] = useState<any[]>([])
  const [showDialog, setShowDialog] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    event_type: 'meeting',
    start_time: '',
    end_time: '',
    attendees: '[]'
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchEvents()
  }, [])

  const fetchEvents = async () => {
    try {
      const data = await projectService.getProjectCalendar(token, project.id)
      setEvents(data)
    } catch (error) {
      console.error('Failed to fetch calendar events', error)
    }
  }

  const handleSubmit = async () => {
    if (!formData.title || !formData.description || !formData.start_time || !formData.end_time) {
      alert('Please fill all required fields')
      return
    }

    setLoading(true)
    try {
      await projectService.createCalendarEvent(token, project.id, formData)
      alert('Event created successfully!')
      setShowDialog(false)
      setFormData({
        title: '',
        description: '',
        event_type: 'meeting',
        start_time: '',
        end_time: '',
        attendees: '[]'
      })
      fetchEvents()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to create event')
    } finally {
      setLoading(false)
    }
  }

  const getEventTypeColor = (eventType: string) => {
    switch (eventType) {
      case 'meeting':
        return 'bg-blue-100 text-blue-700'
      case 'site_visit':
        return 'bg-green-100 text-green-700'
      case 'deadline':
        return 'bg-red-100 text-red-700'
      case 'milestone':
        return 'bg-purple-100 text-purple-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold mb-2">Calendar</h2>
          <p className="text-gray-600">Schedule meetings, site visits, and track important dates</p>
        </div>
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Add Event
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Create Calendar Event</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  placeholder="Event title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Event description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="event_type">Event Type</Label>
                <Select value={formData.event_type} onValueChange={(value) => setFormData({ ...formData, event_type: value })}>
                  <SelectTrigger id="event_type">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="meeting">Meeting</SelectItem>
                    <SelectItem value="site_visit">Site Visit</SelectItem>
                    <SelectItem value="deadline">Deadline</SelectItem>
                    <SelectItem value="milestone">Milestone</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="start_time">Start Time</Label>
                  <Input
                    id="start_time"
                    type="datetime-local"
                    value={formData.start_time}
                    onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="end_time">End Time</Label>
                  <Input
                    id="end_time"
                    type="datetime-local"
                    value={formData.end_time}
                    onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                  />
                </div>
              </div>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSubmit} className="flex-1" disabled={loading}>
                {loading ? 'Creating...' : 'Create Event'}
              </Button>
              <Button onClick={() => setShowDialog(false)} variant="outline" className="flex-1">
                Cancel
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-4">
        {events.map((event) => (
          <Card key={event.id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-3">
                  <CalendarIcon className="w-5 h-5 text-gray-600" />
                  <div>
                    <CardTitle className="text-lg">{event.title}</CardTitle>
                    <span className={`inline-block px-2 py-1 rounded text-xs font-medium mt-1 ${getEventTypeColor(event.event_type)}`}>
                      {event.event_type.replace('_', ' ')}
                    </span>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700 mb-4">{event.description}</p>
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <p className="text-sm text-gray-500">Start Time</p>
                  <p className="font-medium">{new Date(event.start_time).toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">End Time</p>
                  <p className="font-medium">{new Date(event.end_time).toLocaleString()}</p>
                </div>
              </div>
              {event.attendees && Array.isArray(event.attendees) && event.attendees.length > 0 && (
                <div className="mt-3 pt-3 border-t">
                  <p className="text-sm text-gray-500 mb-1">Attendees:</p>
                  <p className="text-sm">{event.attendees.join(', ')}</p>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {events.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            No events scheduled yet. Create an event to track important dates.
          </CardContent>
        </Card>
      )}
    </div>
  )
}
