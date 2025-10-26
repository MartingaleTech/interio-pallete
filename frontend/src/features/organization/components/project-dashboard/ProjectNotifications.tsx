import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Bell, CheckCheck } from 'lucide-react'
import { Project, ProjectNotification } from '../../../../types'
import { projectService } from '../../../../services/projectService'

interface ProjectNotificationsProps {
  project: Project
  token: string
  onUnreadCountChange: (count: number) => void
}

export function ProjectNotifications({ project, token, onUnreadCountChange }: ProjectNotificationsProps) {
  const [notifications, setNotifications] = useState<ProjectNotification[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchNotifications()
  }, [])

  const fetchNotifications = async () => {
    try {
      const data = await projectService.getProjectNotifications(token, project.id)
      setNotifications(data)
      const unreadCount = data.filter((n: ProjectNotification) => !n.is_read).length
      onUnreadCountChange(unreadCount)
    } catch (error) {
      console.error('Failed to fetch notifications', error)
    }
  }

  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await projectService.markNotificationAsRead(token, project.id, notificationId)
      fetchNotifications()
    } catch (error) {
      console.error('Failed to mark notification as read', error)
    }
  }

  const handleMarkAllAsRead = async () => {
    setLoading(true)
    try {
      await projectService.markAllNotificationsAsRead(token, project.id)
      fetchNotifications()
    } catch (error) {
      console.error('Failed to mark all as read', error)
    } finally {
      setLoading(false)
    }
  }

  const unreadNotifications = notifications.filter(n => !n.is_read)
  const readNotifications = notifications.filter(n => n.is_read)

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold mb-2">Notifications</h2>
          <p className="text-gray-600">Stay updated with project notifications</p>
        </div>
        {unreadNotifications.length > 0 && (
          <Button onClick={handleMarkAllAsRead} disabled={loading} variant="outline">
            <CheckCheck className="w-4 h-4 mr-2" />
            Mark All as Read
          </Button>
        )}
      </div>

      {unreadNotifications.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Unread ({unreadNotifications.length})</h3>
          {unreadNotifications.map((notification) => (
            <Card key={notification.id} className="border-l-4 border-l-blue-500 bg-blue-50">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Bell className="w-5 h-5 text-blue-600" />
                  {notification.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 mb-3">{notification.message}</p>
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                  <p className="text-sm text-gray-500">
                    {new Date(notification.created_at).toLocaleString()}
                  </p>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => handleMarkAsRead(notification.id)}
                  >
                    Mark as Read
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {readNotifications.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Read ({readNotifications.length})</h3>
          {readNotifications.map((notification) => (
            <Card key={notification.id} className="opacity-75">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Bell className="w-5 h-5" />
                  {notification.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 mb-3">{notification.message}</p>
                <p className="text-sm text-gray-500">
                  {new Date(notification.created_at).toLocaleString()}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {notifications.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            No notifications yet for this project.
          </CardContent>
        </Card>
      )}
    </div>
  )
}
