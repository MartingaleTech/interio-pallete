import { useState, useEffect } from 'react'
import { organizationService } from '../services/organizationService'
import { Project } from '../types'

export function useProjects(token: string | null) {
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchProjects = async () => {
    if (!token) return
    setIsLoading(true)
    setError(null)
    try {
      const data = await organizationService.getProjects(token)
      setProjects(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch projects')
      console.error('Failed to fetch projects', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchProjects()
  }, [token])

  return { projects, isLoading, error, refetch: fetchProjects }
}
