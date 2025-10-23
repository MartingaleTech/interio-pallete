import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Bell, Check, CheckCheck } from 'lucide-react'
import { adminService, AdminNotification } from '../../../services/adminService'

interface AdminNotificationsProps {
  token: string
}

export function AdminNotifications({ token }: AdminNotificationsProps) {
  const [notifications, setNotifications] = useState<AdminNotification[]>([])
  const [showUnreadOnly, setShowUnreadOnly] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchNotifications()
  }, [token, showUnreadOnly])

  const fetchNotifications = async () => {
    try {
      setLoading(true)
      const data = await adminService.getNotifications(token, showUnreadOnly)
      setNotifications(data)
    } catch (error) {
      console.error('Failed to fetch notifications', error)
    } finally {
      setLoading(false)
    }
  }

  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await adminService.markNotificationRead(token, notificationId)
      fetchNotifications()
    } catch (error) {
      console.error('Failed to mark notification as read', error)
    }
  }

  const handleMarkAllAsRead = async () => {
    try {
      await adminService.markAllNotificationsRead(token)
      fetchNotifications()
    } catch (error) {
      console.error('Failed to mark all notifications as read', error)
    }
  }

  const unreadCount = notifications.filter(n => n.is_read === 0).length

  if (loading) {
    return <div className="p-8">Loading...</div>
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Notifications</h1>
          <p className="text-gray-500 mt-1">
            {unreadCount > 0 ? `${unreadCount} unread notification${unreadCount > 1 ? 's' : ''}` : 'All caught up!'}
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => setShowUnreadOnly(!showUnreadOnly)}
          >
            {showUnreadOnly ? 'Show All' : 'Show Unread Only'}
          </Button>
          {unreadCount > 0 && (
            <Button onClick={handleMarkAllAsRead}>
              <CheckCheck className="w-4 h-4 mr-2" />
              Mark All as Read
            </Button>
          )}
        </div>
      </div>

      <div className="space-y-3">
        {notifications.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <Bell className="w-16 h-16 mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500">No notifications</p>
            </CardContent>
          </Card>
        ) : (
          notifications.map((notification) => (
            <Card 
              key={notification.id}
              className={notification.is_read === 0 ? 'border-l-4 border-l-blue-500 bg-blue-50' : ''}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <CardTitle className="text-base">{notification.title}</CardTitle>
                      {notification.is_read === 0 && (
                        <span className="bg-blue-500 text-white text-xs px-2 py-0.5 rounded">New</span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-2">{notification.message}</p>
                    <p className="text-xs text-gray-400 mt-2">
                      {new Date(notification.created_at).toLocaleString()}
                    </p>
                  </div>
                  {notification.is_read === 0 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleMarkAsRead(notification.id)}
                    >
                      <Check className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              </CardHeader>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
