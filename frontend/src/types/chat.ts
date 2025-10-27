export interface ChatRoom {
  id: string
  project_id: string
  org_id: string
  name: string
  description?: string
  created_by: string
  created_at: string
  updated_at: string
  unread_count?: number
}

export interface ChatMessage {
  id: string
  room_id?: string
  sender_id: string
  sender_name: string
  recipient_id?: string
  message: string
  message_type: string
  attachment_url?: string
  attachment_name?: string
  attachment_type?: string
  attachment_size?: number
  parent_message_id?: string
  mentions?: string
  is_edited: boolean
  edited_at?: string
  is_deleted: boolean
  deleted_at?: string
  created_at: string
  read_receipts?: MessageReadReceipt[]
}

export interface MessageReadReceipt {
  id: string
  message_id: string
  user_id: string
  delivered_at?: string
  read_at?: string
}

export interface TypingStatus {
  user_id: string
  user_name: string
  room_id?: string
  recipient_id?: string
  updated_at: string
}

export interface ChatNotificationSettings {
  email_notifications: boolean
  push_notifications: boolean
  show_read_receipts: boolean
  show_typing_indicators: boolean
}

export interface DirectMessageConversation {
  user_id: string
  user_name: string
  last_message: ChatMessage
  unread_count: number
}

export interface ChatRoomParticipant {
  id: string
  user_id: string
  user_name: string
  user_email: string
  joined_at: string
  last_read_at?: string
  is_admin: boolean
}
