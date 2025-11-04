import { api } from './api'
import { Organization, OrganizationFormData, MemberFormData } from '../types'

export interface AdminStats {
  total_orgs: number
  active_orgs: number
  inactive_orgs: number
  total_projects: number
  total_revenue: number
  pending_tickets: number
}

export interface SupportTicket {
  id: string
  org_id: string
  created_by: string
  subject: string
  description: string
  status: string
  priority: string
  created_at: string
  updated_at: string
}

export interface AdminNotification {
  id: string
  admin_id: string
  org_id: string | null
  notification_type: string
  title: string
  message: string
  is_read: number
  created_at: string
}

export const adminService = {
  async getOrganizations(token: string): Promise<Organization[]> {
    const res = await api.fetchWithAuth('/api/v1/admin/organizations', token)
    
    if (!res.ok) {
      throw new Error('Failed to fetch organizations')
    }
    
    return res.json()
  },

  async getOrganization(token: string, orgId: string): Promise<Organization> {
    const res = await api.fetchWithAuth(`/api/admin/organizations/${orgId}`, token)
    
    if (!res.ok) {
      throw new Error('Failed to fetch organization')
    }
    
    return res.json()
  },

  async createOrganization(token: string, data: OrganizationFormData) {
    const res = await api.fetchWithAuth('/api/v1/admin/organizations', token, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to create organization')
    }
    
    return res.json()
  },

  async updateOrganization(token: string, orgId: string, data: Partial<OrganizationFormData>) {
    const res = await api.fetchWithAuth(`/api/admin/organizations/${orgId}`, token, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to update organization')
    }
    
    return res.json()
  },

  async deleteOrganization(token: string, orgId: string) {
    const res = await api.fetchWithAuth(`/api/admin/organizations/${orgId}`, token, {
      method: 'DELETE'
    })
    
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to delete organization')
    }
    
    return res.json()
  },

  async addOrganizationMember(token: string, orgId: string, data: Omit<MemberFormData, 'org_id'>) {
    const res = await api.fetchWithAuth(`/api/admin/organizations/${orgId}/members`, token, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to add member')
    }
    
    return res.json()
  },

  async getStats(token: string): Promise<AdminStats> {
    const res = await api.fetchWithAuth('/api/v1/admin/stats', token)
    
    if (!res.ok) {
      throw new Error('Failed to fetch stats')
    }
    
    return res.json()
  },

  async getNewlyAddedOrgs(token: string, limit: number = 5): Promise<Organization[]> {
    const res = await api.fetchWithAuth(`/api/admin/organizations/newly-added?limit=${limit}`, token)
    
    if (!res.ok) {
      throw new Error('Failed to fetch newly added organizations')
    }
    
    return res.json()
  },

  async getRecentlyViewedOrgs(token: string, limit: number = 5): Promise<Organization[]> {
    const res = await api.fetchWithAuth(`/api/admin/organizations/recently-viewed?limit=${limit}`, token)
    
    if (!res.ok) {
      throw new Error('Failed to fetch recently viewed organizations')
    }
    
    return res.json()
  },

  async recordOrgView(token: string, orgId: string) {
    const res = await api.fetchWithAuth(`/api/admin/organizations/${orgId}/view`, token, {
      method: 'POST'
    })
    
    if (!res.ok) {
      throw new Error('Failed to record org view')
    }
    
    return res.json()
  },

  async getAllTickets(token: string): Promise<SupportTicket[]> {
    const res = await api.fetchWithAuth('/api/v1/admin/support-tickets', token)
    
    if (!res.ok) {
      throw new Error('Failed to fetch support tickets')
    }
    
    return res.json()
  },

  async getOrgTickets(token: string, orgId: string): Promise<SupportTicket[]> {
    const res = await api.fetchWithAuth(`/api/admin/organizations/${orgId}/support-tickets`, token)
    
    if (!res.ok) {
      throw new Error('Failed to fetch organization tickets')
    }
    
    return res.json()
  },

  async updateTicket(token: string, ticketId: string, updates: { status?: string; priority?: string }) {
    const res = await api.fetchWithAuth(`/api/admin/support-tickets/${ticketId}`, token, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    })
    
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to update ticket')
    }
    
    return res.json()
  },

  async getNotifications(token: string, unreadOnly: boolean = false): Promise<AdminNotification[]> {
    const res = await api.fetchWithAuth(`/api/admin/notifications?unread_only=${unreadOnly}`, token)
    
    if (!res.ok) {
      throw new Error('Failed to fetch notifications')
    }
    
    return res.json()
  },

  async markNotificationRead(token: string, notificationId: string) {
    const res = await api.fetchWithAuth(`/api/admin/notifications/${notificationId}/read`, token, {
      method: 'POST'
    })
    
    if (!res.ok) {
      throw new Error('Failed to mark notification as read')
    }
    
    return res.json()
  },

  async markAllNotificationsRead(token: string) {
    const res = await api.fetchWithAuth('/api/v1/admin/notifications/read-all', token, {
      method: 'POST'
    })
    
    if (!res.ok) {
      throw new Error('Failed to mark all notifications as read')
    }
    
    return res.json()
  },

  async getOrgInvoices(token: string, orgId: string) {
    const res = await api.fetchWithAuth(`/api/admin/organizations/${orgId}/invoices`, token)
    
    if (!res.ok) {
      throw new Error('Failed to fetch organization invoices')
    }
    
    return res.json()
  }
}
