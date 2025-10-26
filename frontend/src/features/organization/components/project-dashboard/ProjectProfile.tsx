import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Project } from '../../../../types'

interface ProjectProfileProps {
  project: Project
  token: string
}

export function ProjectProfile({ project }: ProjectProfileProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Project Profile</h2>
        <p className="text-gray-600">View all details related to this project and client</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Project Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-gray-500">Project Name</p>
              <p className="font-medium">{project.name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Description</p>
              <p className="font-medium">{project.description}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Status</p>
              <span className={`inline-block px-3 py-1 rounded text-sm font-medium ${
                project.status === 'planning' 
                  ? 'bg-yellow-100 text-yellow-700'
                  : project.status === 'in_progress'
                  ? 'bg-blue-100 text-blue-700'
                  : project.status === 'completed'
                  ? 'bg-green-100 text-green-700'
                  : 'bg-gray-100 text-gray-700'
              }`}>
                {project.status}
              </span>
            </div>
            <div>
              <p className="text-sm text-gray-500">Budget</p>
              <p className="font-medium text-lg">₹{project.budget.toLocaleString()}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Timeline</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-gray-500">Start Date</p>
              <p className="font-medium">{new Date(project.start_date).toLocaleDateString()}</p>
            </div>
            {project.end_date && (
              <div>
                <p className="text-sm text-gray-500">End Date</p>
                <p className="font-medium">{new Date(project.end_date).toLocaleDateString()}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Client Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-gray-500">Client Name</p>
              <p className="font-medium">{project.client_name}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
