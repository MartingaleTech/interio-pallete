export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = {
  async fetch(endpoint: string, options: RequestInit = {}) {
    const response = await fetch(`${API_URL}${endpoint}`, options)
    return response
  },

  async fetchWithAuth(endpoint: string, token: string, options: RequestInit = {}) {
    return this.fetch(endpoint, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${token}`
      }
    })
  }
}
