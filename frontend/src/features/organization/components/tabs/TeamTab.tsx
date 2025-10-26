import { useState } from 'react'
import { Plus, Edit, Trash2 } from 'lucide-react'
import { TabsContent } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useAuth } from '../../../../state/AuthContext'
import { organizationService } from '../../../../services/organizationService'
import { TeamMember, OrgTeamMemberFormData } from '../../../../types'

interface TeamTabProps {
  teamMembers: TeamMember[]
  onRefresh: () => void
}

export function TeamTab({ teamMembers, onRefresh }: TeamTabProps) {
  const { token } = useAuth()
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [showEditDialog, setShowEditDialog] = useState(false)
  const [editingMember, setEditingMember] = useState<TeamMember | null>(null)
  const [formData, setFormData] = useState<OrgTeamMemberFormData>({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    role: 'org_member',
    password: ''
  })
  const [isLoading, setIsLoading] = useState(false)

  const handleAdd = async () => {
    if (!token) return
    setIsLoading(true)
    try {
      await organizationService.addOrgTeamMember(token, formData)
      alert('Team member added successfully!')
      setShowAddDialog(false)
      setFormData({ first_name: '', last_name: '', email: '', phone: '', role: 'org_member', password: '' })
      onRefresh()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to add team member')
    } finally {
      setIsLoading(false)
    }
  }

  const handleEdit = async () => {
    if (!token || !editingMember) return
    setIsLoading(true)
    try {
      await organizationService.updateTeamMember(token, editingMember.id, formData)
      alert('Team member updated successfully!')
      setShowEditDialog(false)
      setEditingMember(null)
      setFormData({ first_name: '', last_name: '', email: '', phone: '', role: 'org_member', password: '' })
      onRefresh()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to update team member')
    } finally {
      setIsLoading(false)
    }
  }

  const handleRemove = async (memberId: string) => {
    if (!token || !confirm('Are you sure you want to remove this team member?')) return
    try {
      await organizationService.removeTeamMember(token, memberId)
      alert('Team member removed successfully!')
      onRefresh()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to remove team member')
    }
  }

  const openEditDialog = (member: TeamMember) => {
    setEditingMember(member)
    setFormData({
      first_name: member.first_name || member.name?.split(' ')[0] || '',
      last_name: member.last_name || member.name?.split(' ')[1] || '',
      email: member.email,
      phone: member.phone || '',
      role: member.role,
      password: ''
    })
    setShowEditDialog(true)
  }

  const TeamMemberForm = () => (
    <div className="space-y-4 py-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>First Name</Label>
          <Input
            placeholder="First name"
            value={formData.first_name}
            onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
          />
        </div>
        <div className="space-y-2">
          <Label>Last Name</Label>
          <Input
            placeholder="Last name"
            value={formData.last_name}
            onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label>Email</Label>
        <Input
          type="email"
          placeholder="member@example.com"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        />
      </div>
      <div className="space-y-2">
        <Label>Phone Number</Label>
        <Input
          type="tel"
          placeholder="Phone number"
          value={formData.phone}
          onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
        />
      </div>
      <div className="space-y-2">
        <Label>Role</Label>
        <Select 
          value={formData.role} 
          onValueChange={(value) => setFormData({ ...formData, role: value })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select role" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="org_owner">Owner</SelectItem>
            <SelectItem value="org_member">Member</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        <Label>Password {showEditDialog && '(optional)'}</Label>
        <Input
          type="password"
          placeholder={showEditDialog ? "Leave empty to keep current password" : "Temporary password"}
          value={formData.password}
          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
        />
      </div>
    </div>
  )

  return (
    <TabsContent value="team" className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Team Members</h2>
        <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Add Team Member
            </Button>
          </DialogTrigger>
          <DialogContent 
            className="sm:max-w-lg"
            onOpenAutoFocus={(e) => e.preventDefault()}
            onPointerDownOutside={(e) => e.preventDefault()}
          >
            <DialogHeader>
              <DialogTitle>Add Team Member</DialogTitle>
              <DialogDescription>
                Add a new team member to your organization
              </DialogDescription>
            </DialogHeader>
            <TeamMemberForm />
            <div className="flex gap-2">
              <Button onClick={handleAdd} className="flex-1" disabled={isLoading}>
                {isLoading ? 'Adding...' : 'Add Member'}
              </Button>
              <Button onClick={() => setShowAddDialog(false)} variant="outline" className="flex-1">
                Cancel
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>First Name</TableHead>
                <TableHead>Last Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Phone Number</TableHead>
                <TableHead>Role</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {teamMembers.map((member) => (
                <TableRow key={member.id}>
                  <TableCell>{member.first_name || member.name?.split(' ')[0] || '-'}</TableCell>
                  <TableCell>{member.last_name || member.name?.split(' ')[1] || '-'}</TableCell>
                  <TableCell>{member.email}</TableCell>
                  <TableCell>{member.phone || '-'}</TableCell>
                  <TableCell>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      member.role === 'org_owner' 
                        ? 'bg-purple-100 text-purple-700' 
                        : 'bg-blue-100 text-blue-700'
                    }`}>
                      {member.role === 'org_owner' ? 'Owner' : 'Member'}
                    </span>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => openEditDialog(member)}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => handleRemove(member.id)}
                      >
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          {teamMembers.length === 0 && (
            <div className="py-12 text-center text-gray-500">
              No team members yet. Click "Add Team Member" to add one.
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent 
          className="sm:max-w-lg"
          onOpenAutoFocus={(e) => e.preventDefault()}
          onPointerDownOutside={(e) => e.preventDefault()}
        >
          <DialogHeader>
            <DialogTitle>Edit Team Member</DialogTitle>
            <DialogDescription>
              Update team member information
            </DialogDescription>
          </DialogHeader>
          <TeamMemberForm />
          <div className="flex gap-2">
            <Button onClick={handleEdit} className="flex-1" disabled={isLoading}>
              {isLoading ? 'Updating...' : 'Update Member'}
            </Button>
            <Button onClick={() => setShowEditDialog(false)} variant="outline" className="flex-1">
              Cancel
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </TabsContent>
  )
}
