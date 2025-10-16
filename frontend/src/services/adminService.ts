import { api } from './api'
import { Organization, OrganizationFormData, MemberFormData } from '../types'

export const adminService = {
  async getOrganizations(token: string): Promise<Organization[]> {
    const res = await api.fetchWithAuth('/api/admin/organizations', token)
    
    if (!res.ok) {
      throw new Error('Failed to fetch organizations')
    }
    
    return res.json()
  },

  async createOrganization(token: string, data: OrganizationFormData) {
    const res = await api.fetchWithAuth('/api/admin/organizations', token, {
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
  }
}
