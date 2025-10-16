import { api } from './api'
import { Project } from '../types'

export const clientService = {
  async getProjects(token: string): Promise<Project[]> {
    const res = await api.fetchWithAuth('/api/clients/projects', token)
    if (!res.ok) throw new Error('Failed to fetch projects')
    return res.json()
  }
}
