import { api } from './api'
import { 
  Project, 
  Client, 
  TeamMember, 
  ClientFormData, 
  ProjectFormData,
  TeamMemberFormData,
  EventFormData,
  DesignFormData,
  InvoiceFormData,
  OrgTeamMemberFormData
} from '../types'

export const organizationService = {
  async getProjects(token: string): Promise<Project[]> {
    const res = await api.fetchWithAuth('/api/v1/organizations/projects', token)
    if (!res.ok) throw new Error('Failed to fetch projects')
    return res.json()
  },

  async createProject(token: string, data: ProjectFormData) {
    const res = await api.fetchWithAuth('/api/v1/organizations/projects', token, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...data,
        budget: parseFloat(data.budget)
      })
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to create project')
    }
    return res.json()
  },

  async getClients(token: string): Promise<Client[]> {
    const res = await api.fetchWithAuth('/api/v1/organizations/clients', token)
    if (!res.ok) throw new Error('Failed to fetch clients')
    return res.json()
  },

  async createClient(token: string, data: ClientFormData) {
    const res = await api.fetchWithAuth('/api/v1/organizations/clients', token, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to create client')
    }
    return res.json()
  },

  async getTeamMembers(token: string): Promise<TeamMember[]> {
    const res = await api.fetchWithAuth('/api/v1/organizations/members', token)
    if (!res.ok) throw new Error('Failed to fetch team members')
    return res.json()
  },

  async addProjectTeamMember(token: string, projectId: string, data: Omit<TeamMemberFormData, 'project_id'>) {
    const res = await api.fetchWithAuth(`/api/organizations/projects/${projectId}/team`, token, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to add team member')
    }
    return res.json()
  },

  async addOrgTeamMember(token: string, data: OrgTeamMemberFormData) {
    const res = await api.fetchWithAuth('/api/v1/organizations/members', token, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to add team member')
    }
    return res.json()
  },

  async updateTeamMember(token: string, memberId: string, data: OrgTeamMemberFormData) {
    const res = await api.fetchWithAuth(`/api/organizations/members/${memberId}`, token, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to update team member')
    }
    return res.json()
  },

  async removeTeamMember(token: string, memberId: string) {
    const res = await api.fetchWithAuth(`/api/organizations/members/${memberId}`, token, {
      method: 'DELETE'
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to remove team member')
    }
    return res.json()
  },

  async createEvent(token: string, data: EventFormData) {
    const res = await api.fetchWithAuth('/api/v1/organizations/calendar/events', token, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to create event')
    }
    return res.json()
  },

  async uploadDesign(token: string, data: DesignFormData) {
    const formData = new FormData()
    formData.append('project_id', data.project_id)
    formData.append('title', data.title)
    formData.append('description', data.description)
    if (data.file) {
      formData.append('file', data.file)
    }
    
    const res = await api.fetchWithAuth('/api/v1/organizations/designs', token, {
      method: 'POST',
      body: formData
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to upload design')
    }
    return res.json()
  },

  async createInvoice(token: string, data: InvoiceFormData) {
    const res = await api.fetchWithAuth('/api/v1/organizations/invoices', token, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...data,
        amount: parseFloat(data.amount)
      })
    })
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to create invoice')
    }
    return res.json()
  }
}
