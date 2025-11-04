import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, Trash2, Eye } from 'lucide-react'
import { adminService } from '../../../services/adminService'
import { Organization } from '../../../types'
import { CreateOrganizationForm } from './CreateOrganizationForm'

interface AdminOrganizationsListProps {
  token: string
  onSelectOrg: (orgId: string) => void
}

export function AdminOrganizationsList({ token, onSelectOrg }: AdminOrganizationsListProps) {
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [showAddOrg, setShowAddOrg] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchOrganizations()
  }, [token])

  const fetchOrganizations = async () => {
    try {
      setLoading(true)
      const data = await adminService.getOrganizations(token)
      setOrganizations(data)
    } catch (error) {
      console.error('Failed to fetch organizations', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (orgId: string, orgName: string) => {
    if (!confirm(`Are you sure you want to delete ${orgName}? This action cannot be undone.`)) {
      return
    }

    try {
      await adminService.deleteOrganization(token, orgId)
      fetchOrganizations()
    } catch (error) {
      console.error('Failed to delete organization', error)
      alert('Failed to delete organization')
    }
  }

  const handleOrganizationCreated = () => {
    setShowAddOrg(false)
    fetchOrganizations()
  }

  if (loading) {
    return <div className="p-8">Loading...</div>
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Organizations</h1>
          <p className="text-gray-500 mt-1">Manage all organizations on the platform</p>
        </div>
        <Button onClick={() => setShowAddOrg(!showAddOrg)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Organization
        </Button>
      </div>

      {showAddOrg && (
        <CreateOrganizationForm 
          onSuccess={handleOrganizationCreated}
          onCancel={() => setShowAddOrg(false)}
        />
      )}

      <Card>
        <CardHeader>
          <CardTitle>All Organizations ({organizations.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3 font-medium">Name</th>
                  <th className="text-left p-3 font-medium">Location</th>
                  <th className="text-left p-3 font-medium">Email</th>
                  <th className="text-left p-3 font-medium">Phone</th>
                  <th className="text-left p-3 font-medium">Plan</th>
                  <th className="text-left p-3 font-medium">Status</th>
                  <th className="text-right p-3 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {organizations.map((org) => (
                  <tr key={org.id} className="border-b hover:bg-gray-50">
                    <td className="p-3 font-medium">{org.name}</td>
                    <td className="p-3 text-sm text-gray-600">{org.city}, {org.state}</td>
                    <td className="p-3 text-sm text-gray-600">{org.email}</td>
                    <td className="p-3 text-sm text-gray-600">{org.phone}</td>
                    <td className="p-3 text-sm">{org.subscription_plan}</td>
                    <td className="p-3">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        org.subscription_status === 'active' 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-red-100 text-red-700'
                      }`}>
                        {org.subscription_status}
                      </span>
                    </td>
                    <td className="p-3">
                      <div className="flex items-center justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onSelectOrg(org.id)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(org.id, org.name)}
                        >
                          <Trash2 className="w-4 h-4 text-red-600" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {organizations.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                No organizations yet. Click "Add Organization" to create one.
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
