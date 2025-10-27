import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react'
import { ChatRoom, ChatMessage, TypingStatus, DirectMessageConversation } from '../types/chat'
import { chatWebSocketService } from '../services/chatWebSocketService'
import { chatService } from '../services/chatService'
import { useAuth } from './AuthContext'

interface ChatContextType {
  rooms: ChatRoom[]
  currentRoom: ChatRoom | null
  currentMessages: ChatMessage[]
  directConversations: DirectMessageConversation[]
  currentDirectUserId: string | null
  typingUsers: TypingStatus[]
  isConnected: boolean
  setCurrentRoom: (room: ChatRoom | null) => void
  setCurrentDirectUserId: (userId: string | null) => void
  loadRooms: () => Promise<void>
  loadRoomMessages: (roomId: string) => Promise<void>
  loadDirectMessages: (userId: string) => Promise<void>
  loadDirectConversations: () => Promise<void>
  sendMessage: (roomId: string, message: string) => void
  sendDirectMessage: (recipientId: string, message: string) => void
  editMessage: (messageId: string, message: string) => void
  deleteMessage: (messageId: string, deleteForEveryone?: boolean) => void
  startTyping: (roomId?: string, recipientId?: string) => void
  stopTyping: (roomId?: string, recipientId?: string) => void
  markAsRead: (messageIds: string[], roomId?: string) => void
  joinRoom: (roomId: string) => void
  leaveRoom: (roomId: string) => void
}

const ChatContext = createContext<ChatContextType | undefined>(undefined)

export function ChatProvider({ children }: { children: ReactNode }) {
  const { token, user } = useAuth()
  const [rooms, setRooms] = useState<ChatRoom[]>([])
  const [currentRoom, setCurrentRoom] = useState<ChatRoom | null>(null)
  const [currentMessages, setCurrentMessages] = useState<ChatMessage[]>([])
  const [directConversations, setDirectConversations] = useState<DirectMessageConversation[]>([])
  const [currentDirectUserId, setCurrentDirectUserId] = useState<string | null>(null)
  const [typingUsers, setTypingUsers] = useState<TypingStatus[]>([])
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    if (token && user) {
      chatWebSocketService.connect(token)
      setIsConnected(true)

      const unsubscribe = chatWebSocketService.onMessage((message) => {
        switch (message.type) {
          case 'message_received':
            handleMessageReceived(message.payload)
            break
          case 'message_edited':
            handleMessageEdited(message.payload)
            break
          case 'message_deleted':
            handleMessageDeleted(message.payload)
            break
          case 'typing_status':
            handleTypingStatus(message.payload)
            break
          case 'message_read':
            handleMessageRead(message.payload)
            break
          case 'message_delivered':
            handleMessageDelivered(message.payload)
            break
          case 'error':
            console.error('WebSocket error:', message.payload)
            break
        }
      })

      return () => {
        unsubscribe()
        chatWebSocketService.disconnect()
        setIsConnected(false)
      }
    }
  }, [token, user])

  const handleMessageReceived = useCallback((payload: any) => {
    const newMessage: ChatMessage = payload.message
    
    setCurrentMessages(prev => {
      const exists = prev.some(m => m.id === newMessage.id)
      if (exists) return prev
      return [...prev, newMessage]
    })

    if (newMessage.room_id) {
      setRooms(prev => prev.map(room => {
        if (room.id === newMessage.room_id) {
          return {
            ...room,
            updated_at: newMessage.created_at,
            unread_count: (room.unread_count || 0) + (newMessage.sender_id !== user?.id ? 1 : 0)
          }
        }
        return room
      }))
    } else {
      loadDirectConversations()
    }
  }, [user])

  const handleMessageEdited = useCallback((payload: any) => {
    const editedMessage: ChatMessage = payload.message
    setCurrentMessages(prev => prev.map(m => 
      m.id === editedMessage.id ? editedMessage : m
    ))
  }, [])

  const handleMessageDeleted = useCallback((payload: any) => {
    const messageId: string = payload.message_id
    setCurrentMessages(prev => prev.map(m => 
      m.id === messageId ? { ...m, is_deleted: true, message: 'This message was deleted' } : m
    ))
  }, [])

  const handleTypingStatus = useCallback((payload: any) => {
    const status: TypingStatus = payload
    
    if (status.user_id === user?.id) return

    setTypingUsers(prev => {
      const filtered = prev.filter(t => t.user_id !== status.user_id)
      
      if (payload.is_typing) {
        return [...filtered, status]
      }
      
      return filtered
    })

    setTimeout(() => {
      setTypingUsers(prev => prev.filter(t => t.user_id !== status.user_id))
    }, 5000)
  }, [user])

  const handleMessageRead = useCallback((payload: any) => {
    const { message_id, user_id } = payload
    setCurrentMessages(prev => prev.map(m => {
      if (m.id === message_id) {
        const receipts = m.read_receipts || []
        const existingReceipt = receipts.find(r => r.user_id === user_id)
        if (existingReceipt) {
          return {
            ...m,
            read_receipts: receipts.map(r => 
              r.user_id === user_id ? { ...r, read_at: new Date().toISOString() } : r
            )
          }
        } else {
          return {
            ...m,
            read_receipts: [...receipts, {
              id: '',
              message_id,
              user_id,
              read_at: new Date().toISOString()
            }]
          }
        }
      }
      return m
    }))
  }, [])

  const handleMessageDelivered = useCallback((payload: any) => {
    const { message_id, user_id } = payload
    setCurrentMessages(prev => prev.map(m => {
      if (m.id === message_id) {
        const receipts = m.read_receipts || []
        const existingReceipt = receipts.find(r => r.user_id === user_id)
        if (!existingReceipt) {
          return {
            ...m,
            read_receipts: [...receipts, {
              id: '',
              message_id,
              user_id,
              delivered_at: new Date().toISOString()
            }]
          }
        }
      }
      return m
    }))
  }, [])

  const loadRooms = useCallback(async () => {
    if (!token) return
    try {
      const fetchedRooms = await chatService.getChatRooms(token)
      setRooms(fetchedRooms)
    } catch (error) {
      console.error('Failed to load chat rooms:', error)
    }
  }, [token])

  const loadRoomMessages = useCallback(async (roomId: string) => {
    if (!token) return
    try {
      const { messages } = await chatService.getRoomMessages(token, roomId)
      setCurrentMessages(messages)
      
      const messageIds = messages
        .filter(m => m.sender_id !== user?.id && !m.read_receipts?.some(r => r.user_id === user?.id && r.read_at))
        .map(m => m.id)
      
      if (messageIds.length > 0) {
        markAsRead(messageIds, roomId)
      }
    } catch (error) {
      console.error('Failed to load room messages:', error)
    }
  }, [token, user])

  const loadDirectMessages = useCallback(async (userId: string) => {
    if (!token) return
    try {
      const { messages } = await chatService.getDirectMessages(token, userId)
      setCurrentMessages(messages)
      
      const messageIds = messages
        .filter(m => m.sender_id !== user?.id && !m.read_receipts?.some(r => r.user_id === user?.id && r.read_at))
        .map(m => m.id)
      
      if (messageIds.length > 0) {
        markAsRead(messageIds)
      }
    } catch (error) {
      console.error('Failed to load direct messages:', error)
    }
  }, [token, user])

  const loadDirectConversations = useCallback(async () => {
    if (!token) return
    try {
      const conversations = await chatService.getDirectMessageConversations(token)
      setDirectConversations(conversations)
    } catch (error) {
      console.error('Failed to load direct conversations:', error)
    }
  }, [token])

  const sendMessage = useCallback((roomId: string, message: string) => {
    chatWebSocketService.sendMessage(roomId, message)
  }, [])

  const sendDirectMessage = useCallback((recipientId: string, message: string) => {
    chatWebSocketService.sendDirectMessage(recipientId, message)
  }, [])

  const editMessage = useCallback((messageId: string, message: string) => {
    chatWebSocketService.editMessage(messageId, message)
  }, [])

  const deleteMessage = useCallback((messageId: string, deleteForEveryone: boolean = false) => {
    chatWebSocketService.deleteMessage(messageId, deleteForEveryone)
  }, [])

  const startTyping = useCallback((roomId?: string, recipientId?: string) => {
    chatWebSocketService.startTyping(roomId, recipientId)
  }, [])

  const stopTyping = useCallback((roomId?: string, recipientId?: string) => {
    chatWebSocketService.stopTyping(roomId, recipientId)
  }, [])

  const markAsRead = useCallback((messageIds: string[], roomId?: string) => {
    chatWebSocketService.markAsRead(messageIds, roomId)
  }, [])

  const joinRoom = useCallback((roomId: string) => {
    chatWebSocketService.joinRoom(roomId)
  }, [])

  const leaveRoom = useCallback((roomId: string) => {
    chatWebSocketService.leaveRoom(roomId)
  }, [])

  useEffect(() => {
    if (currentRoom) {
      joinRoom(currentRoom.id)
      loadRoomMessages(currentRoom.id)
      
      return () => {
        leaveRoom(currentRoom.id)
      }
    }
  }, [currentRoom, joinRoom, leaveRoom, loadRoomMessages])

  useEffect(() => {
    if (currentDirectUserId) {
      loadDirectMessages(currentDirectUserId)
    }
  }, [currentDirectUserId, loadDirectMessages])

  return (
    <ChatContext.Provider value={{
      rooms,
      currentRoom,
      currentMessages,
      directConversations,
      currentDirectUserId,
      typingUsers,
      isConnected,
      setCurrentRoom,
      setCurrentDirectUserId,
      loadRooms,
      loadRoomMessages,
      loadDirectMessages,
      loadDirectConversations,
      sendMessage,
      sendDirectMessage,
      editMessage,
      deleteMessage,
      startTyping,
      stopTyping,
      markAsRead,
      joinRoom,
      leaveRoom
    }}>
      {children}
    </ChatContext.Provider>
  )
}

export function useChat() {
  const context = useContext(ChatContext)
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider')
  }
  return context
}
