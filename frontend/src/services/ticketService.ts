import { api } from './api'
import { 
  ProjectTicket,
  ProjectTicketWithDetails,
  ProjectTicketFormData,
  OrgTicket,
  OrgTicketWithDetails,
  OrgTicketFormData,
  TicketCommentFormData,
  TicketAttachmentFormData
} from '../types'
import { toItems } from './pagination'

export const ticketService = {
  async getProjectTickets(token: string, projectId: string): Promise<ProjectTicket[]> {
    const res = await api.fetchWithAuth(`/api/v1/projects/${projectId}/tickets`, token)
    if (!res.ok) throw new Error('Failed to fetch project tickets')
    const data = await res.json()
    return toItems(data)
  },

  async getProjectTicket(token: string, projectId: string, ticketId: string): Promise<ProjectTicketWithDetails> {
    const res = await api.fetchWithAuth(`/api/v1/projects/${projectId}/tickets/${ticketId}`, token)
    if (!res.ok) throw new Error('Failed to fetch project ticket')
    return res.json()
  },

  async createProjectTicket(token: string, projectId: string, data: ProjectTicketFormData): Promise<ProjectTicket> {
    const res = await api.fetchWithAuth(`/api/v1/projects/${projectId}/tickets`, token, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to create project ticket')
    }
    return res.json()
  },

  async updateProjectTicket(token: string, projectId: string, ticketId: string, data: Partial<ProjectTicketFormData> & { status?: string, assigned_to?: string }): Promise<ProjectTicket> {
    const res = await api.fetchWithAuth(`/api/v1/projects/${projectId}/tickets/${ticketId}`, token, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to update project ticket')
    }
    return res.json()
  },

  async deleteProjectTicket(token: string, projectId: string, ticketId: string): Promise<void> {
    const res = await api.fetchWithAuth(`/api/v1/projects/${projectId}/tickets/${ticketId}`, token, {
      method: 'DELETE'
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to delete project ticket')
    }
  },

  async addProjectTicketComment(token: string, projectId: string, ticketId: string, data: TicketCommentFormData) {
    const res = await api.fetchWithAuth(`/api/v1/projects/${projectId}/tickets/${ticketId}/comments`, token, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to add comment')
    }
    return res.json()
  },

  async addProjectTicketAttachment(token: string, projectId: string, ticketId: string, data: TicketAttachmentFormData) {
    const res = await api.fetchWithAuth(`/api/v1/projects/${projectId}/tickets/${ticketId}/attachments`, token, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to add attachment')
    }
    return res.json()
  },

  async getOrgTickets(token: string): Promise<OrgTicket[]> {
    const res = await api.fetchWithAuth('/api/v1/organizations/tickets', token)
    if (!res.ok) throw new Error('Failed to fetch org tickets')
    const data = await res.json()
    return toItems(data)
  },

  async getOrgTicket(token: string, ticketId: string): Promise<OrgTicketWithDetails> {
    const res = await api.fetchWithAuth(`/api/v1/organizations/tickets/${ticketId}`, token)
    if (!res.ok) throw new Error('Failed to fetch org ticket')
    return res.json()
  },

  async createOrgTicket(token: string, data: OrgTicketFormData): Promise<OrgTicket> {
    const res = await api.fetchWithAuth('/api/v1/organizations/tickets', token, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to create org ticket')
    }
    return res.json()
  },

  async updateOrgTicket(token: string, ticketId: string, data: Partial<OrgTicketFormData> & { status?: string, assigned_to?: string }): Promise<OrgTicket> {
    const res = await api.fetchWithAuth(`/api/v1/organizations/tickets/${ticketId}`, token, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to update org ticket')
    }
    return res.json()
  },

  async deleteOrgTicket(token: string, ticketId: string): Promise<void> {
    const res = await api.fetchWithAuth(`/api/v1/organizations/tickets/${ticketId}`, token, {
      method: 'DELETE'
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to delete org ticket')
    }
  },

  async addOrgTicketComment(token: string, ticketId: string, data: TicketCommentFormData) {
    const res = await api.fetchWithAuth(`/api/v1/organizations/tickets/${ticketId}/comments`, token, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to add comment')
    }
    return res.json()
  },

  async addOrgTicketAttachment(token: string, ticketId: string, data: TicketAttachmentFormData) {
    const res = await api.fetchWithAuth(`/api/v1/organizations/tickets/${ticketId}/attachments`, token, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to add attachment')
    }
    return res.json()
  },

  async getAllOrgTickets(token: string): Promise<OrgTicket[]> {
    const res = await api.fetchWithAuth('/api/v1/admin/tickets', token)
    if (!res.ok) throw new Error('Failed to fetch all org tickets')
    const data = await res.json()
    return toItems(data)
  },

  async getMyAssignedTickets(token: string): Promise<OrgTicket[]> {
    const res = await api.fetchWithAuth('/api/v1/admin/tickets/assigned', token)
    if (!res.ok) throw new Error('Failed to fetch assigned tickets')
    const data = await res.json()
    return toItems(data)
  },

  async getOrgTicketAdmin(token: string, ticketId: string): Promise<OrgTicketWithDetails> {
    const res = await api.fetchWithAuth(`/api/v1/admin/tickets/${ticketId}`, token)
    if (!res.ok) throw new Error('Failed to fetch org ticket')
    return res.json()
  },

  async updateOrgTicketAdmin(token: string, ticketId: string, data: Partial<OrgTicketFormData> & { status?: string, assigned_to?: string }): Promise<OrgTicket> {
    const res = await api.fetchWithAuth(`/api/v1/admin/tickets/${ticketId}`, token, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to update org ticket')
    }
    return res.json()
  },

  async addOrgTicketCommentAdmin(token: string, ticketId: string, data: TicketCommentFormData) {
    const res = await api.fetchWithAuth(`/api/v1/admin/tickets/${ticketId}/comments`, token, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to add comment')
    }
    return res.json()
  },

  async getMyAssignedProjectTickets(token: string): Promise<ProjectTicket[]> {
    const res = await api.fetchWithAuth('/api/v1/my-tickets/assigned', token)
    if (!res.ok) throw new Error('Failed to fetch my assigned tickets')
    const data = await res.json()
    return toItems(data)
  }
}
