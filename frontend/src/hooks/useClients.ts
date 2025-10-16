import { useState, useEffect } from 'react'
import { organizationService } from '../services/organizationService'
import { Client } from '../types'

export function useClients(token: string | null) {
  const [clients, setClients] = useState<Client[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchClients = async () => {
    if (!token) return
    setIsLoading(true)
    setError(null)
    try {
      const data = await organizationService.getClients(token)
      setClients(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch clients')
      console.error('Failed to fetch clients', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchClients()
  }, [token])

  return { clients, isLoading, error, refetch: fetchClients }
}
