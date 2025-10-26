import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Plus, Users as UsersIcon } from 'lucide-react'
import { Project, TeamMember } from '../../../../types'
import { projectService } from '../../../../services/projectService'
import { organizationService } from '../../../../services/organizationService'

interface ProjectTeamProps {
  project: Project
  token: string
}

export function ProjectTeam({ project, token }: ProjectTeamProps) {
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([])
  const [orgMembers, setOrgMembers] = useState<TeamMember[]>([])
  const [showDialog, setShowDialog] = useState(false)
  const [formData, setFormData] = useState({
    user_id: '',
    role: ''
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchTeamMembers()
    fetchOrgMembers()
  }, [])

  const fetchTeamMembers = async () => {
    try {
      const data = await projectService.getProjectTeam(token, project.id)
      setTeamMembers(data)
    } catch (error) {
      console.error('Failed to fetch team members', error)
    }
  }

  const fetchOrgMembers = async () => {
    try {
      const data = await organizationService.getTeamMembers(token)
      setOrgMembers(data)
    } catch (error) {
      console.error('Failed to fetch org members', error)
    }
  }

  const handleSubmit = async () => {
    if (!formData.user_id || !formData.role) {
      alert('Please fill all fields')
      return
    }

    setLoading(true)
    try {
      await projectService.addTeamMember(token, project.id, formData)
      alert('Team member added successfully!')
      setShowDialog(false)
      setFormData({ user_id: '', role: '' })
      fetchTeamMembers()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to add team member')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold mb-2">Team Members</h2>
          <p className="text-gray-600">Manage team members assigned to this project</p>
        </div>
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Add Team Member
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Add Team Member</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="member">Team Member</Label>
                <Select value={formData.user_id} onValueChange={(value) => setFormData({ ...formData, user_id: value })}>
                  <SelectTrigger id="member">
                    <SelectValue placeholder="Select a team member" />
                  </SelectTrigger>
                  <SelectContent>
                    {orgMembers.map((member) => (
                      <SelectItem key={member.id} value={member.id}>
                        {member.name || `${member.first_name} ${member.last_name}`}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="role">Role in Project</Label>
                <Input
                  id="role"
                  placeholder="e.g., Designer, Project Manager"
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSubmit} className="flex-1" disabled={loading}>
                {loading ? 'Adding...' : 'Add Member'}
              </Button>
              <Button onClick={() => setShowDialog(false)} variant="outline" className="flex-1">
                Cancel
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {teamMembers.map((member) => (
          <Card key={member.id}>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <UsersIcon className="w-5 h-5" />
                {member.name}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div>
                  <p className="text-sm text-gray-500">Role</p>
                  <p className="font-medium">{member.role}</p>
                </div>
                {member.email && (
                  <div>
                    <p className="text-sm text-gray-500">Email</p>
                    <p className="text-sm truncate">{member.email}</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {teamMembers.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            No team members assigned yet. Add team members to this project.
          </CardContent>
        </Card>
      )}
    </div>
  )
}
