import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Organization } from '../../../types'

interface OrganizationCardProps {
  organization: Organization
}

export function OrganizationCard({ organization }: OrganizationCardProps) {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <CardTitle className="text-lg">{organization.name}</CardTitle>
        <CardDescription>{organization.city}, {organization.state}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="text-sm">
          <span className="font-medium">Email:</span> {organization.email}
        </div>
        <div className="text-sm">
          <span className="font-medium">Phone:</span> {organization.phone}
        </div>
        <div className="text-sm">
          <span className="font-medium">Plan:</span> {organization.subscription_plan}
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-2 py-1 rounded text-xs font-medium ${
            organization.subscription_status === 'active' 
              ? 'bg-green-100 text-green-700' 
              : 'bg-red-100 text-red-700'
          }`}>
            {organization.subscription_status}
          </span>
        </div>
      </CardContent>
    </Card>
  )
}
