"""
Chat Service Layer
Handles business logic for chat operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import re

from src.repositories.chat_repository import (
    ChatRoomRepository,
    ChatRoomParticipantRepository,
    ChatMessageRepository,
    MessageReadReceiptRepository,
    TypingStatusRepository,
    ChatNotificationSettingsRepository
)
from src.repositories.user_repository import UserRepository
from src.repositories.project_repository import ProjectRepository
from src.database.models import User, ChatRoom, ChatMessage
from src.models.chat import (
    CreateChatRoomRequest,
    SendMessageRequest,
    SendDirectMessageRequest,
    EditMessageRequest,
    AddParticipantRequest,
    UpdateNotificationSettingsRequest,
    TypingStatusRequest,
    SearchMessagesRequest
)


class ChatService:
    """Service for chat operations"""
    
    def __init__(self):
        self.room_repo = ChatRoomRepository()
        self.participant_repo = ChatRoomParticipantRepository()
        self.message_repo = ChatMessageRepository()
        self.receipt_repo = MessageReadReceiptRepository()
        self.typing_repo = TypingStatusRepository()
        self.settings_repo = ChatNotificationSettingsRepository()
    
    
    def create_chat_room(self, db: Session, user: User, request: CreateChatRoomRequest) -> ChatRoom:
        """Create a new chat room for a project"""
        project_repo = ProjectRepository(db)
        project = project_repo.get_by_id(request.project_id)
        if not project:
            raise ValueError("Project not found")
        
        role_value = getattr(user.role, 'value', user.role)
        if project.org_id != user.org_id and role_value != "admin":
            raise ValueError("Access denied to this project")
        
        existing_room = self.room_repo.get_by_project_id(db, request.project_id)
        if existing_room:
            return existing_room
        
        room_data = {
            "id": str(uuid.uuid4()),
            "project_id": request.project_id,
            "org_id": project.org_id,
            "name": request.name,
            "description": request.description,
            "created_by": user.id
        }
        
        room = self.room_repo.create(db, room_data)
        
        self.add_participant_to_room(db, room.id, user.id, is_admin=True)
        
        return room
    
    def get_chat_room(self, db: Session, user: User, room_id: str) -> Optional[ChatRoom]:
        """Get chat room by ID"""
        room = self.room_repo.get_by_id(db, room_id)
        if not room:
            return None
        
        if not self.participant_repo.is_participant(db, room_id, user.id):
            role_value = getattr(user.role, 'value', user.role)
            if role_value != "admin":
                raise ValueError("Access denied to this chat room")
        
        return room
    
    def get_user_chat_rooms(self, db: Session, user: User) -> List[ChatRoom]:
        """Get all chat rooms for a user"""
        rooms = self.room_repo.get_rooms_for_user(db, user.id, user.org_id)
        
        for room in rooms:
            participant = self.participant_repo.get_participant(db, room.id, user.id)
            if participant:
                unread_count = self.message_repo.get_unread_count(
                    db, room.id, user.id, participant.last_read_at
                )
                room.unread_count = unread_count
        
        return rooms
    
    def add_participant_to_room(self, db: Session, room_id: str, user_id: str, is_admin: bool = False) -> bool:
        """Add a participant to a chat room"""
        if self.participant_repo.is_participant(db, room_id, user_id):
            return True
        
        participant_data = {
            "id": str(uuid.uuid4()),
            "room_id": room_id,
            "user_id": user_id,
            "is_admin": is_admin
        }
        
        self.participant_repo.add_participant(db, participant_data)
        return True
    
    def remove_participant_from_room(self, db: Session, user: User, room_id: str, user_id: str) -> bool:
        """Remove a participant from a chat room"""
        participant = self.participant_repo.get_participant(db, room_id, user.id)
        if not participant or not participant.is_admin:
            role_value = getattr(user.role, 'value', user.role)
            if role_value != "admin":
                raise ValueError("Only room admins can remove participants")
        
        return self.participant_repo.remove_participant(db, room_id, user_id)
    
    def get_room_participants(self, db: Session, user: User, room_id: str) -> List[Dict[str, Any]]:
        """Get all participants in a chat room"""
        if not self.participant_repo.is_participant(db, room_id, user.id):
            role_value = getattr(user.role, 'value', user.role)
            if role_value != "admin":
                raise ValueError("Access denied to this chat room")
        
        participants = self.participant_repo.get_participants(db, room_id)
        
        result = []
        user_repo = UserRepository(db)
        for participant in participants:
            user_info = user_repo.get_by_id(participant.user_id)
            if user_info:
                result.append({
                    "id": participant.id,
                    "user_id": participant.user_id,
                    "user_name": user_info.name,
                    "user_email": user_info.email,
                    "joined_at": participant.joined_at,
                    "last_read_at": participant.last_read_at,
                    "is_admin": participant.is_admin
                })
        
        return result
    
    
    def send_message(self, db: Session, user: User, room_id: str, request: SendMessageRequest) -> ChatMessage:
        """Send a message to a chat room"""
        if not self.participant_repo.is_participant(db, room_id, user.id):
            raise ValueError("You are not a participant in this chat room")
        
        mentions = self._extract_mentions(request.message)
        if request.mentions:
            mentions.extend(request.mentions)
        
        message_data = {
            "id": str(uuid.uuid4()),
            "room_id": room_id,
            "sender_id": user.id,
            "sender_name": user.name,
            "message": request.message,
            "message_type": request.message_type,
            "attachment_url": request.attachment_url,
            "attachment_name": request.attachment_name,
            "attachment_type": request.attachment_type,
            "attachment_size": request.attachment_size,
            "parent_message_id": request.parent_message_id,
            "mentions": ",".join(mentions) if mentions else None
        }
        
        message = self.message_repo.create(db, message_data)
        
        room = self.room_repo.get_by_id(db, room_id)
        if room:
            self.room_repo.update(db, room_id, {"updated_at": datetime.utcnow()})
        
        participants = self.participant_repo.get_participants(db, room_id)
        for participant in participants:
            if participant.user_id != user.id:
                self.receipt_repo.mark_as_delivered(db, message.id, participant.user_id)
        
        return message
    
    def send_direct_message(self, db: Session, user: User, request: SendDirectMessageRequest) -> ChatMessage:
        """Send a direct message to another user"""
        user_repo = UserRepository(db)
        recipient = user_repo.get_by_id(request.recipient_id)
        if not recipient:
            raise ValueError("Recipient not found")
        
        role_value = getattr(user.role, 'value', user.role)
        if user.org_id != recipient.org_id and role_value != "admin":
            raise ValueError("Cannot send direct message to user in different organization")
        
        message_data = {
            "id": str(uuid.uuid4()),
            "room_id": None,
            "sender_id": user.id,
            "sender_name": user.name,
            "recipient_id": request.recipient_id,
            "message": request.message,
            "message_type": request.message_type,
            "attachment_url": request.attachment_url,
            "attachment_name": request.attachment_name,
            "attachment_type": request.attachment_type,
            "attachment_size": request.attachment_size
        }
        
        message = self.message_repo.create(db, message_data)
        
        self.receipt_repo.mark_as_delivered(db, message.id, request.recipient_id)
        
        return message
    
    def edit_message(self, db: Session, user: User, message_id: str, request: EditMessageRequest) -> ChatMessage:
        """Edit a message"""
        message = self.message_repo.get_by_id(db, message_id)
        if not message:
            raise ValueError("Message not found")
        
        if message.sender_id != user.id:
            raise ValueError("You can only edit your own messages")
        
        if message.is_deleted:
            raise ValueError("Cannot edit deleted message")
        
        update_data = {
            "message": request.message,
            "is_edited": True,
            "edited_at": datetime.utcnow()
        }
        
        return self.message_repo.update(db, message_id, update_data)
    
    def delete_message(self, db: Session, user: User, message_id: str, delete_for_everyone: bool = False) -> bool:
        """Delete a message"""
        message = self.message_repo.get_by_id(db, message_id)
        if not message:
            raise ValueError("Message not found")
        
        if message.sender_id != user.id:
            if message.room_id:
                participant = self.participant_repo.get_participant(db, message.room_id, user.id)
                if not participant or not participant.is_admin:
                    role_value = getattr(user.role, 'value', user.role)
                    if role_value != "admin":
                        raise ValueError("You can only delete your own messages")
            else:
                raise ValueError("You can only delete your own messages")
        
        return self.message_repo.soft_delete(db, message_id, delete_for_everyone)
    
    def get_room_messages(
        self, 
        db: Session, 
        user: User, 
        room_id: str, 
        limit: int = 50, 
        offset: int = 0,
        before_timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get messages in a chat room with pagination"""
        if not self.participant_repo.is_participant(db, room_id, user.id):
            role_value = getattr(user.role, 'value', user.role)
            if role_value != "admin":
                raise ValueError("Access denied to this chat room")
        
        messages = self.message_repo.get_room_messages(db, room_id, limit, offset, before_timestamp)
        
        for message in messages:
            receipts = self.receipt_repo.get_receipts_for_message(db, message.id)
            message.read_receipts = receipts
        
        has_more = len(messages) == limit
        
        return {
            "messages": list(reversed(messages)),  # Reverse to show oldest first
            "has_more": has_more
        }
    
    def get_direct_messages(
        self, 
        db: Session, 
        user: User, 
        other_user_id: str, 
        limit: int = 50, 
        offset: int = 0,
        before_timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get direct messages between two users"""
        messages = self.message_repo.get_direct_messages(
            db, user.id, other_user_id, limit, offset, before_timestamp
        )
        
        for message in messages:
            receipts = self.receipt_repo.get_receipts_for_message(db, message.id)
            message.read_receipts = receipts
        
        has_more = len(messages) == limit
        
        return {
            "messages": list(reversed(messages)),  # Reverse to show oldest first
            "has_more": has_more
        }
    
    def mark_messages_as_read(self, db: Session, user: User, room_id: Optional[str], message_ids: List[str]) -> bool:
        """Mark messages as read"""
        for message_id in message_ids:
            message = self.message_repo.get_by_id(db, message_id)
            if message and message.sender_id != user.id:
                self.receipt_repo.mark_as_read(db, message_id, user.id)
        
        if room_id:
            self.participant_repo.update_last_read(db, room_id, user.id)
        
        return True
    
    def search_messages(self, db: Session, user: User, request: SearchMessagesRequest) -> List[ChatMessage]:
        """Search messages by keyword"""
        if request.room_id:
            if not self.participant_repo.is_participant(db, request.room_id, user.id):
                role_value = getattr(user.role, 'value', user.role)
                if role_value != "admin":
                    raise ValueError("Access denied to this chat room")
        
        return self.message_repo.search_messages(
            db, request.room_id, user.id, request.query, request.limit
        )
    
    
    def set_typing_status(self, db: Session, user: User, request: TypingStatusRequest) -> bool:
        """Set typing status"""
        typing_data = {
            "id": str(uuid.uuid4()),
            "user_id": user.id,
            "room_id": request.room_id,
            "recipient_id": request.recipient_id,
            "is_typing": request.is_typing
        }
        
        self.typing_repo.set_typing(db, typing_data)
        return True
    
    def get_typing_users(self, db: Session, room_id: Optional[str] = None, recipient_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get users currently typing"""
        typing_statuses = self.typing_repo.get_typing_users(db, room_id, recipient_id)
        
        result = []
        user_repo = UserRepository(db)
        for status in typing_statuses:
            user_info = user_repo.get_by_id(status.user_id)
            if user_info:
                result.append({
                    "user_id": status.user_id,
                    "user_name": user_info.name,
                    "room_id": status.room_id,
                    "recipient_id": status.recipient_id,
                    "updated_at": status.updated_at
                })
        
        return result
    
    
    def get_notification_settings(self, db: Session, user: User) -> Dict[str, Any]:
        """Get notification settings for user"""
        settings = self.settings_repo.get_or_create(db, user.id)
        return {
            "email_notifications": settings.email_notifications,
            "push_notifications": settings.push_notifications,
            "show_read_receipts": settings.show_read_receipts,
            "show_typing_indicators": settings.show_typing_indicators
        }
    
    def update_notification_settings(self, db: Session, user: User, request: UpdateNotificationSettingsRequest) -> Dict[str, Any]:
        """Update notification settings for user"""
        update_data = {}
        if request.email_notifications is not None:
            update_data["email_notifications"] = request.email_notifications
        if request.push_notifications is not None:
            update_data["push_notifications"] = request.push_notifications
        if request.show_read_receipts is not None:
            update_data["show_read_receipts"] = request.show_read_receipts
        if request.show_typing_indicators is not None:
            update_data["show_typing_indicators"] = request.show_typing_indicators
        
        settings = self.settings_repo.update(db, user.id, update_data)
        if not settings:
            settings = self.settings_repo.get_or_create(db, user.id)
        
        return {
            "email_notifications": settings.email_notifications,
            "push_notifications": settings.push_notifications,
            "show_read_receipts": settings.show_read_receipts,
            "show_typing_indicators": settings.show_typing_indicators
        }
    
    
    def _extract_mentions(self, message: str) -> List[str]:
        """Extract @mentions from message text"""
        pattern = r'@(\w+)'
        matches = re.findall(pattern, message)
        return matches
    
    def get_unread_count(self, db: Session, user: User, room_id: Optional[str] = None) -> int:
        """Get unread message count for user"""
        if room_id:
            participant = self.participant_repo.get_participant(db, room_id, user.id)
            if participant:
                return self.message_repo.get_unread_count(
                    db, room_id, user.id, participant.last_read_at
                )
        return 0
    
    def get_direct_message_conversations(self, db: Session, user: User) -> List[Dict[str, Any]]:
        """Get list of direct message conversations for user"""
        all_messages = db.query(ChatMessage).filter(
            and_(
                ChatMessage.room_id == None,
                or_(
                    ChatMessage.sender_id == user.id,
                    ChatMessage.recipient_id == user.id
                ),
                ChatMessage.is_deleted == False
            )
        ).order_by(desc(ChatMessage.created_at)).all()
        
        conversations = {}
        user_repo = UserRepository(db)
        for message in all_messages:
            partner_id = message.recipient_id if message.sender_id == user.id else message.sender_id
            if partner_id not in conversations:
                partner = user_repo.get_by_id(partner_id)
                if partner:
                    conversations[partner_id] = {
                        "user_id": partner_id,
                        "user_name": partner.name,
                        "last_message": message,
                        "unread_count": 0
                    }
        
        for partner_id in conversations:
            unread = db.query(ChatMessage).filter(
                and_(
                    ChatMessage.room_id == None,
                    ChatMessage.sender_id == partner_id,
                    ChatMessage.recipient_id == user.id,
                    ChatMessage.is_deleted == False
                )
            ).outerjoin(
                MessageReadReceipt,
                and_(
                    MessageReadReceipt.message_id == ChatMessage.id,
                    MessageReadReceipt.user_id == user.id
                )
            ).filter(MessageReadReceipt.read_at == None).count()
            
            conversations[partner_id]["unread_count"] = unread
        
        return list(conversations.values())
