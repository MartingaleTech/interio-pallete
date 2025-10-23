import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Building2, TrendingUp, FolderOpen, DollarSign, AlertCircle } from 'lucide-react'
import { adminService, AdminStats } from '../../../services/adminService'
import { Organization } from '../../../types'
import { OrganizationCard } from './OrganizationCard'

interface AdminOverviewProps {
  token: string
  onSelectOrg: (orgId: string) => void
}

export function AdminOverview({ token, onSelectOrg }: AdminOverviewProps) {
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [newlyAdded, setNewlyAdded] = useState<Organization[]>([])
  const [recentlyViewed, setRecentlyViewed] = useState<Organization[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [token])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [statsData, newlyAddedData, recentlyViewedData] = await Promise.all([
        adminService.getStats(token),
        adminService.getNewlyAddedOrgs(token, 5),
        adminService.getRecentlyViewedOrgs(token, 5)
      ])
      
      setStats(statsData)
      setNewlyAdded(newlyAddedData)
      setRecentlyViewed(recentlyViewedData)
    } catch (error) {
      console.error('Failed to fetch overview data', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="p-8">Loading...</div>
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard Overview</h1>
        <p className="text-gray-500 mt-1">Welcome to the admin dashboard</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Organizations</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_orgs || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.active_orgs || 0} active, {stats?.inactive_orgs || 0} inactive
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Projects</CardTitle>
            <FolderOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_projects || 0}</div>
            <p className="text-xs text-muted-foreground">Across all organizations</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₹{stats?.total_revenue?.toLocaleString() || 0}</div>
            <p className="text-xs text-muted-foreground">From paid invoices</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Tickets</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.pending_tickets || 0}</div>
            <p className="text-xs text-muted-foreground">Require attention</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Newly Added Organizations</CardTitle>
            <CardDescription>Recently created organizations</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {newlyAdded.length === 0 ? (
              <p className="text-sm text-gray-500">No organizations yet</p>
            ) : (
              newlyAdded.map((org) => (
                <div
                  key={org.id}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                  onClick={() => onSelectOrg(org.id)}
                >
                  <div>
                    <p className="font-medium">{org.name}</p>
                    <p className="text-sm text-gray-500">{org.city}, {org.state}</p>
                  </div>
                  <Button variant="ghost" size="sm">View</Button>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recently Viewed Organizations</CardTitle>
            <CardDescription>Organizations you recently accessed</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {recentlyViewed.length === 0 ? (
              <p className="text-sm text-gray-500">No recently viewed organizations</p>
            ) : (
              recentlyViewed.map((org) => (
                <div
                  key={org.id}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                  onClick={() => onSelectOrg(org.id)}
                >
                  <div>
                    <p className="font-medium">{org.name}</p>
                    <p className="text-sm text-gray-500">{org.city}, {org.state}</p>
                  </div>
                  <Button variant="ghost" size="sm">View</Button>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
