import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { BarChart3 } from 'lucide-react'

export function AdminAnalytics() {
  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Analytics</h1>
        <p className="text-gray-500 mt-1">Platform insights and metrics</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Analytics Dashboard</CardTitle>
          <CardDescription>Coming Soon</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-16">
            <BarChart3 className="w-20 h-20 mx-auto text-gray-300 mb-4" />
            <p className="text-gray-500 mb-2">Advanced analytics will be available soon</p>
            <p className="text-sm text-gray-400">
              Track revenue trends, user engagement, and platform growth metrics
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
