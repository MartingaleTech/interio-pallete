import { ChatRoom, ChatMessage, ChatNotificationSettings, DirectMessageConversation, ChatRoomParticipant } from '../types/chat'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const chatService = {
  async createChatRoom(token: string, projectId: string, name: string, description?: string): Promise<ChatRoom> {
    const response = await fetch(`${API_URL}/api/v1/chat/rooms`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        project_id: projectId,
        name,
        description
      })
    })

    if (!response.ok) {
      throw new Error('Failed to create chat room')
    }

    return response.json()
  },

  async getChatRooms(token: string): Promise<ChatRoom[]> {
    const response = await fetch(`${API_URL}/api/v1/chat/rooms`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('Failed to fetch chat rooms')
    }

    return response.json()
  },

  async getChatRoom(token: string, roomId: string): Promise<ChatRoom> {
    const response = await fetch(`${API_URL}/api/v1/chat/rooms/${roomId}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('Failed to fetch chat room')
    }

    return response.json()
  },

  async getRoomMessages(token: string, roomId: string, limit: number = 50, offset: number = 0, beforeTimestamp?: string): Promise<{ messages: ChatMessage[], has_more: boolean }> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString()
    })

    if (beforeTimestamp) {
      params.append('before_timestamp', beforeTimestamp)
    }

    const response = await fetch(`${API_URL}/api/v1/chat/rooms/${roomId}/messages?${params}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('Failed to fetch room messages')
    }

    return response.json()
  },

  async getDirectMessages(token: string, userId: string, limit: number = 50, offset: number = 0, beforeTimestamp?: string): Promise<{ messages: ChatMessage[], has_more: boolean }> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString()
    })

    if (beforeTimestamp) {
      params.append('before_timestamp', beforeTimestamp)
    }

    const response = await fetch(`${API_URL}/api/v1/chat/direct/${userId}/messages?${params}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('Failed to fetch direct messages')
    }

    return response.json()
  },

  async getDirectMessageConversations(token: string): Promise<DirectMessageConversation[]> {
    const response = await fetch(`${API_URL}/api/v1/chat/direct/conversations`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('Failed to fetch direct message conversations')
    }

    return response.json()
  },

  async getOrgMembers(token: string): Promise<Array<{ id: string, name: string, email: string, role: string }>> {
    const response = await fetch(`${API_URL}/api/v1/chat/org/members`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('Failed to fetch org members')
    }

    return response.json()
  },

  async searchMessages(token: string, query: string, roomId?: string, limit: number = 50): Promise<ChatMessage[]> {
    const response = await fetch(`${API_URL}/api/v1/chat/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        query,
        room_id: roomId,
        limit
      })
    })

    if (!response.ok) {
      throw new Error('Failed to search messages')
    }

    return response.json()
  },

  async getRoomParticipants(token: string, roomId: string): Promise<ChatRoomParticipant[]> {
    const response = await fetch(`${API_URL}/api/v1/chat/rooms/${roomId}/participants`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('Failed to fetch room participants')
    }

    return response.json()
  },

  async addParticipant(token: string, roomId: string, userId: string, isAdmin: boolean = false): Promise<void> {
    const response = await fetch(`${API_URL}/api/v1/chat/rooms/${roomId}/participants`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        user_id: userId,
        is_admin: isAdmin
      })
    })

    if (!response.ok) {
      throw new Error('Failed to add participant')
    }
  },

  async removeParticipant(token: string, roomId: string, userId: string): Promise<void> {
    const response = await fetch(`${API_URL}/api/v1/chat/rooms/${roomId}/participants/${userId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('Failed to remove participant')
    }
  },

  async getUnreadCount(token: string, roomId: string): Promise<number> {
    const response = await fetch(`${API_URL}/api/v1/chat/rooms/${roomId}/unread`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('Failed to fetch unread count')
    }

    const data = await response.json()
    return data.unread_count
  },

  async getNotificationSettings(token: string): Promise<ChatNotificationSettings> {
    const response = await fetch(`${API_URL}/api/v1/chat/settings`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('Failed to fetch notification settings')
    }

    return response.json()
  },

  async updateNotificationSettings(token: string, settings: Partial<ChatNotificationSettings>): Promise<ChatNotificationSettings> {
    const response = await fetch(`${API_URL}/api/v1/chat/settings`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(settings)
    })

    if (!response.ok) {
      throw new Error('Failed to update notification settings')
    }

    return response.json()
  }
}
