import { useState } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useAuth } from '../../../state/AuthContext'
import { adminService } from '../../../services/adminService'
import { Organization, MemberFormData } from '../../../types'

interface AddMemberDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  organizations: Organization[]
  onSuccess: () => void
}

export function AddMemberDialog({ open, onOpenChange, organizations, onSuccess }: AddMemberDialogProps) {
  const { token } = useAuth()
  const [formData, setFormData] = useState<MemberFormData>({
    org_id: '',
    name: '',
    email: '',
    phone: '',
    password: '',
    role: 'org_member'
  })
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async () => {
    if (!token || !formData.org_id) return
    setIsLoading(true)
    try {
      await adminService.addOrganizationMember(token, formData.org_id, {
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
        password: formData.password,
        role: formData.role
      })
      alert('Organization member added successfully!')
      setFormData({ org_id: '', name: '', email: '', phone: '', password: '', role: 'org_member' })
      onOpenChange(false)
      onSuccess()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to add member')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add Organization Member</DialogTitle>
          <DialogDescription>
            Add a new member to an existing organization
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="member-org">Organization</Label>
            <Select 
              value={formData.org_id} 
              onValueChange={(value) => setFormData({ ...formData, org_id: value })}
            >
              <SelectTrigger id="member-org">
                <SelectValue placeholder="Select organization" />
              </SelectTrigger>
              <SelectContent>
                {organizations.map((org) => (
                  <SelectItem key={org.id} value={org.id}>
                    {org.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="member-name">Name</Label>
            <Input
              id="member-name"
              placeholder="Member name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="member-email">Email</Label>
            <Input
              id="member-email"
              type="email"
              placeholder="member@example.com"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="member-phone">Phone</Label>
            <Input
              id="member-phone"
              type="tel"
              placeholder="Phone number"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="member-password">Password</Label>
            <Input
              id="member-password"
              type="password"
              placeholder="Temporary password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="member-role">Role</Label>
            <Select 
              value={formData.role} 
              onValueChange={(value) => setFormData({ ...formData, role: value })}
            >
              <SelectTrigger id="member-role">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="org_member">Member</SelectItem>
                <SelectItem value="org_owner">Owner</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleSubmit} className="flex-1" disabled={isLoading}>
            {isLoading ? 'Adding...' : 'Add Member'}
          </Button>
          <Button onClick={() => onOpenChange(false)} variant="outline" className="flex-1">
            Cancel
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
