
type WSMessageType = 
  | 'send_message'
  | 'edit_message'
  | 'delete_message'
  | 'typing_start'
  | 'typing_stop'
  | 'mark_read'
  | 'join_room'
  | 'leave_room'
  | 'new_message'
  | 'message_received'
  | 'message_edited'
  | 'message_deleted'
  | 'typing_status'
  | 'message_read'
  | 'message_delivered'
  | 'error'

interface WSMessage {
  type: WSMessageType
  payload: any
}

type MessageHandler = (message: WSMessage) => void
type ConnectionHandler = (connected: boolean) => void

class ChatWebSocketService {
  private ws: WebSocket | null = null
  private token: string | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private messageHandlers: Set<MessageHandler> = new Set()
  private connectionHandlers: Set<ConnectionHandler> = new Set()
  private isConnecting = false
  private shouldReconnect = true

  connect(token: string) {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return
    }

    this.token = token
    this.isConnecting = true
    this.shouldReconnect = true

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
    const url = `${wsUrl}/ws/chat?token=${token}`

    try {
      this.ws = new WebSocket(url)

      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.isConnecting = false
        this.reconnectAttempts = 0
        this.connectionHandlers.forEach(handler => handler(true))
      }

      this.ws.onmessage = (event) => {
        try {
          const incoming = JSON.parse(event.data)
          console.log('[WS] Raw incoming:', incoming)
          const normalized: WSMessage = {
            type: incoming.type,
            payload: incoming.payload ?? incoming.data
          }
          console.log('[WS] Normalized:', normalized)
          this.messageHandlers.forEach(handler => handler(normalized))
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.isConnecting = false
      }

      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        this.isConnecting = false
        this.ws = null
        this.connectionHandlers.forEach(handler => handler(false))

        if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++
          const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
          console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`)
          setTimeout(() => {
            if (this.token) {
              this.connect(this.token)
            }
          }, delay)
        }
      }
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      this.isConnecting = false
    }
  }

  disconnect() {
    this.shouldReconnect = false
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.token = null
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  onMessage(handler: MessageHandler) {
    this.messageHandlers.add(handler)
    return () => {
      this.messageHandlers.delete(handler)
    }
  }

  onConnectionChange(handler: ConnectionHandler) {
    this.connectionHandlers.add(handler)
    return () => {
      this.connectionHandlers.delete(handler)
    }
  }

  private send(message: WSMessage) {
    if (!this.isConnected()) {
      console.error('WebSocket is not connected')
      return
    }

    try {
      const backendMessage = {
        type: message.type,
        data: message.payload
      }
      console.log('Sending WebSocket message:', backendMessage)
      this.ws?.send(JSON.stringify(backendMessage))
    } catch (error) {
      console.error('Failed to send WebSocket message:', error)
    }
  }

  sendMessage(roomId: string, message: string, messageType: string = 'text', attachmentUrl?: string, attachmentName?: string, attachmentType?: string, attachmentSize?: number, parentMessageId?: string, mentions?: string[]) {
    this.send({
      type: 'send_message',
      payload: {
        room_id: roomId,
        message,
        message_type: messageType,
        attachment_url: attachmentUrl,
        attachment_name: attachmentName,
        attachment_type: attachmentType,
        attachment_size: attachmentSize,
        parent_message_id: parentMessageId,
        mentions
      }
    })
  }

  sendDirectMessage(recipientId: string, message: string, messageType: string = 'text', attachmentUrl?: string, attachmentName?: string, attachmentType?: string, attachmentSize?: number) {
    this.send({
      type: 'send_message',
      payload: {
        recipient_id: recipientId,
        message,
        message_type: messageType,
        attachment_url: attachmentUrl,
        attachment_name: attachmentName,
        attachment_type: attachmentType,
        attachment_size: attachmentSize
      }
    })
  }

  editMessage(messageId: string, message: string) {
    this.send({
      type: 'edit_message',
      payload: {
        message_id: messageId,
        message
      }
    })
  }

  deleteMessage(messageId: string, deleteForEveryone: boolean = false) {
    this.send({
      type: 'delete_message',
      payload: {
        message_id: messageId,
        delete_for_everyone: deleteForEveryone
      }
    })
  }

  startTyping(roomId?: string, recipientId?: string) {
    this.send({
      type: 'typing_start',
      payload: {
        room_id: roomId,
        recipient_id: recipientId
      }
    })
  }

  stopTyping(roomId?: string, recipientId?: string) {
    this.send({
      type: 'typing_stop',
      payload: {
        room_id: roomId,
        recipient_id: recipientId
      }
    })
  }

  markAsRead(messageIds: string[], roomId?: string) {
    this.send({
      type: 'mark_read',
      payload: {
        message_ids: messageIds,
        room_id: roomId
      }
    })
  }

  joinRoom(roomId: string) {
    this.send({
      type: 'join_room',
      payload: {
        room_id: roomId
      }
    })
  }

  leaveRoom(roomId: string) {
    this.send({
      type: 'leave_room',
      payload: {
        room_id: roomId
      }
    })
  }
}

export const chatWebSocketService = new ChatWebSocketService()
