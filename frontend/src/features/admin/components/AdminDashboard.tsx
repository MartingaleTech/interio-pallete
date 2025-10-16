import { useState, useEffect } from 'react'
import { Plus, UserPlus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { DashboardHeader } from '../../../components/shared/DashboardHeader'
import { useAuth } from '../../../state/AuthContext'
import { adminService } from '../../../services/adminService'
import { Organization } from '../../../types'
import { CreateOrganizationForm } from './CreateOrganizationForm'
import { AddMemberDialog } from './AddMemberDialog'
import { OrganizationCard } from './OrganizationCard'

export function AdminDashboard() {
  const { user, logout, token } = useAuth()
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [showAddOrg, setShowAddOrg] = useState(false)
  const [showAddMember, setShowAddMember] = useState(false)

  useEffect(() => {
    if (token) {
      fetchOrganizations()
    }
  }, [token])

  const fetchOrganizations = async () => {
    if (!token) return
    try {
      const data = await adminService.getOrganizations(token)
      setOrganizations(data)
    } catch (error) {
      console.error('Failed to fetch organizations', error)
    }
  }

  const handleOrganizationCreated = () => {
    setShowAddOrg(false)
    fetchOrganizations()
  }

  if (!user) return null

  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardHeader 
        title="Admin Dashboard" 
        userName={user.name} 
        onLogout={logout} 
      />

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold">Organizations</h2>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setShowAddMember(true)}>
              <UserPlus className="w-4 h-4 mr-2" />
              Add Member
            </Button>
            <Button onClick={() => setShowAddOrg(!showAddOrg)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Organization
            </Button>
          </div>
        </div>

        {showAddOrg && (
          <CreateOrganizationForm 
            onSuccess={handleOrganizationCreated}
            onCancel={() => setShowAddOrg(false)}
          />
        )}

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {organizations.map((org) => (
            <OrganizationCard key={org.id} organization={org} />
          ))}
        </div>

        {organizations.length === 0 && !showAddOrg && (
          <Card>
            <CardContent className="py-12 text-center text-gray-500">
              No organizations yet. Click "Add Organization" to create one.
            </CardContent>
          </Card>
        )}

        <AddMemberDialog
          open={showAddMember}
          onOpenChange={setShowAddMember}
          organizations={organizations}
          onSuccess={fetchOrganizations}
        />
      </main>
    </div>
  )
}
