import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuth } from '../../../state/AuthContext'
import { adminService } from '../../../services/adminService'
import { OrganizationFormData } from '../../../types'

interface CreateOrganizationFormProps {
  onSuccess: () => void
  onCancel: () => void
}

export function CreateOrganizationForm({ onSuccess, onCancel }: CreateOrganizationFormProps) {
  const { token } = useAuth()
  const [formData, setFormData] = useState<OrganizationFormData>({
    name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    pincode: '',
    owner_email: '',
    owner_name: '',
    owner_phone: '',
    owner_password: '',
    subscription_plan: 'basic'
  })
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async () => {
    if (!token) return
    setIsLoading(true)
    try {
      await adminService.createOrganization(token, formData)
      alert('Organization created successfully!')
      onSuccess()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to create organization')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>Create New Organization</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Organization Name</label>
            <Input
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Organization Email</label>
            <Input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Organization Phone</label>
            <Input
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">City</label>
            <Input
              value={formData.city}
              onChange={(e) => setFormData({ ...formData, city: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">State</label>
            <Input
              value={formData.state}
              onChange={(e) => setFormData({ ...formData, state: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Pincode</label>
            <Input
              value={formData.pincode}
              onChange={(e) => setFormData({ ...formData, pincode: e.target.value })}
            />
          </div>
          <div className="col-span-2 space-y-2">
            <label className="text-sm font-medium">Address</label>
            <Input
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Owner Name</label>
            <Input
              value={formData.owner_name}
              onChange={(e) => setFormData({ ...formData, owner_name: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Owner Email</label>
            <Input
              type="email"
              value={formData.owner_email}
              onChange={(e) => setFormData({ ...formData, owner_email: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Owner Phone</label>
            <Input
              value={formData.owner_phone}
              onChange={(e) => setFormData({ ...formData, owner_phone: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Owner Password</label>
            <Input
              type="password"
              value={formData.owner_password}
              onChange={(e) => setFormData({ ...formData, owner_password: e.target.value })}
            />
          </div>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleSubmit} disabled={isLoading}>
            {isLoading ? 'Creating...' : 'Create Organization'}
          </Button>
          <Button onClick={onCancel} variant="outline" disabled={isLoading}>
            Cancel
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
