import { api } from './api'
import { User } from '../types'

export const authService = {
  async login(email: string, password: string) {
    const res = await api.fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })
    
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Invalid email or password')
    }
    
    return res.json()
  },

  async requestOtp(phone: string) {
    const res = await api.fetch('/api/auth/phone/request-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone })
    })
    
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Failed to send OTP')
    }
    
    return res.json()
  },

  async verifyOtp(phone: string, otp: string) {
    const res = await api.fetch('/api/auth/phone/verify-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, otp })
    })
    
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.detail || 'Invalid OTP')
    }
    
    return res.json()
  },

  async getCurrentUser(token: string): Promise<User> {
    const res = await api.fetchWithAuth('/api/auth/me', token)
    
    if (!res.ok) {
      throw new Error('Failed to fetch user')
    }
    
    return res.json()
  }
}
