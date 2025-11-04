const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const projectService = {
  async getProjectNotifications(token: string, projectId: string) {
    const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/notifications`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to fetch notifications')
    return res.json()
  },

  async getUnreadNotifications(token: string, projectId: string) {
    const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/notifications/unread`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to fetch unread notifications')
    return res.json()
  },

  async markNotificationAsRead(token: string, projectId: string, notificationId: string) {
    const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/notifications/${notificationId}/read`, {
      method: 'PATCH',
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to mark notification as read')
    return res.json()
  },

  async markAllNotificationsAsRead(token: string, projectId: string) {
    const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/notifications/mark-all-read`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to mark all notifications as read')
    return res.json()
  },

  async getDailyUpdates(token: string, projectId: string) {
    const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/daily-updates`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to fetch daily updates')
    return res.json()
  },

  async createDailyUpdate(token: string, projectId: string, data: any) {
    const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/daily-updates`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(data)
    })
    if (!res.ok) throw new Error('Failed to create daily update')
    return res.json()
  },

  async updateDailyUpdate(token: string, projectId: string, updateId: string, data: any) {
    const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/daily-updates/${updateId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(data)
    })
    if (!res.ok) throw new Error('Failed to update daily update')
    return res.json()
  },

  async deleteDailyUpdate(token: string, projectId: string, updateId: string) {
    const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/daily-updates/${updateId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to delete daily update')
    return res.json()
  },

  async getProjectTickets(token: string, projectId: string) {
    const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/tickets`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to fetch tickets')
    return res.json()
  },

  async createProjectTicket(token: string, projectId: string, data: any) {
    const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/tickets`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(data)
    })
    if (!res.ok) throw new Error('Failed to create ticket')
    return res.json()
  },

  async getProjectTeam(token: string, projectId: string) {
    const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/team`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to fetch team members')
    return res.json()
  },

  async addTeamMember(token: string, projectId: string, data: any) {
    const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/team`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(data)
    })
    if (!res.ok) throw new Error('Failed to add team member')
    return res.json()
  },

  async getProjectCalendar(token: string, projectId: string) {
    const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/calendar`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to fetch calendar events')
    return res.json()
  },

  async createCalendarEvent(token: string, projectId: string, data: any) {
    const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/calendar`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(data)
    })
    if (!res.ok) throw new Error('Failed to create calendar event')
    return res.json()
  },

  async getProjectDesigns(token: string, projectId: string) {
    const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/designs`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to fetch designs')
    return res.json()
  },

  async createProjectDesign(token: string, projectId: string, data: any) {
    const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/designs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(data)
    })
    if (!res.ok) throw new Error('Failed to create design')
    return res.json()
  },

  async getProjectInvoices(token: string, projectId: string) {
    const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/invoices`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to fetch invoices')
    return res.json()
  },

  async createProjectInvoice(token: string, projectId: string, data: any) {
    const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/invoices`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(data)
    })
    if (!res.ok) throw new Error('Failed to create invoice')
    return res.json()
  }
}
