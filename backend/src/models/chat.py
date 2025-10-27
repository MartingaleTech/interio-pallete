"""
Pydantic models for Chat API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CreateChatRoomRequest(BaseModel):
    project_id: str
    name: str
    description: Optional[str] = None


class SendMessageRequest(BaseModel):
    message: str
    message_type: str = "text"
    attachment_url: Optional[str] = None
    attachment_name: Optional[str] = None
    attachment_type: Optional[str] = None
    attachment_size: Optional[int] = None
    parent_message_id: Optional[str] = None
    mentions: Optional[List[str]] = None


class SendDirectMessageRequest(BaseModel):
    recipient_id: str
    message: str
    message_type: str = "text"
    attachment_url: Optional[str] = None
    attachment_name: Optional[str] = None
    attachment_type: Optional[str] = None
    attachment_size: Optional[int] = None


class EditMessageRequest(BaseModel):
    message: str


class AddParticipantRequest(BaseModel):
    user_id: str
    is_admin: bool = False


class UpdateNotificationSettingsRequest(BaseModel):
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    show_read_receipts: Optional[bool] = None
    show_typing_indicators: Optional[bool] = None


class TypingStatusRequest(BaseModel):
    is_typing: bool
    room_id: Optional[str] = None
    recipient_id: Optional[str] = None


class SearchMessagesRequest(BaseModel):
    query: str
    room_id: Optional[str] = None
    limit: int = 50


class ChatRoomParticipantResponse(BaseModel):
    id: str
    user_id: str
    joined_at: datetime
    last_read_at: Optional[datetime]
    is_admin: bool
    
    class Config:
        from_attributes = True


class ChatRoomResponse(BaseModel):
    id: str
    project_id: str
    org_id: str
    name: str
    description: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    participants: Optional[List[ChatRoomParticipantResponse]] = None
    unread_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


class MessageReadReceiptResponse(BaseModel):
    id: str
    user_id: str
    read_at: datetime
    delivered_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ChatMessageResponse(BaseModel):
    id: str
    room_id: Optional[str]
    sender_id: str
    sender_name: str
    recipient_id: Optional[str]
    message: str
    message_type: str
    attachment_url: Optional[str]
    attachment_name: Optional[str]
    attachment_type: Optional[str]
    attachment_size: Optional[int]
    is_edited: bool
    edited_at: Optional[datetime]
    is_deleted: bool
    deleted_at: Optional[datetime]
    parent_message_id: Optional[str]
    mentions: Optional[str]
    created_at: datetime
    updated_at: datetime
    read_receipts: Optional[List[MessageReadReceiptResponse]] = None
    
    class Config:
        from_attributes = True


class TypingStatusResponse(BaseModel):
    user_id: str
    room_id: Optional[str]
    recipient_id: Optional[str]
    is_typing: bool
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChatNotificationSettingsResponse(BaseModel):
    id: str
    user_id: str
    email_notifications: bool
    push_notifications: bool
    show_read_receipts: bool
    show_typing_indicators: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DirectMessageConversationResponse(BaseModel):
    user_id: str
    user_name: str
    last_message: Optional[ChatMessageResponse]
    unread_count: int


class MessageHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]
    total_count: int
    has_more: bool


class UnreadCountResponse(BaseModel):
    room_id: Optional[str]
    recipient_id: Optional[str]
    unread_count: int


class WSMessageType:
    SEND_MESSAGE = "send_message"
    EDIT_MESSAGE = "edit_message"
    DELETE_MESSAGE = "delete_message"
    TYPING_START = "typing_start"
    TYPING_STOP = "typing_stop"
    MARK_READ = "mark_read"
    JOIN_ROOM = "join_room"
    LEAVE_ROOM = "leave_room"
    
    NEW_MESSAGE = "new_message"
    MESSAGE_EDITED = "message_edited"
    MESSAGE_DELETED = "message_deleted"
    USER_TYPING = "user_typing"
    USER_STOPPED_TYPING = "user_stopped_typing"
    MESSAGE_READ = "message_read"
    MESSAGE_DELIVERED = "message_delivered"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    ERROR = "error"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


class WSMessage(BaseModel):
    type: str
    data: dict
    timestamp: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class WSErrorMessage(BaseModel):
    type: str = WSMessageType.ERROR
    error: str
    details: Optional[str] = None
