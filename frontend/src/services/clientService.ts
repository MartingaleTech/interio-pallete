import { api } from './api'
import { Project } from '../types'
import { toItems } from './pagination'

export const clientService = {
  async getProjects(token: string): Promise<Project[]> {
    const res = await api.fetchWithAuth('/api/v1/clients/projects', token)
    if (!res.ok) throw new Error('Failed to fetch projects')
    const data = await res.json()
    return toItems(data)
  }
}
