"""
Chat Repository Layer
Handles data access for chat-related operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional
from datetime import datetime, timezone
from src.database.models import (
    ChatRoom, ChatRoomParticipant, ChatMessage, 
    MessageReadReceipt, TypingStatus, ChatNotificationSettings
)


class ChatRoomRepository:
    """Repository for ChatRoom operations"""
    
    def create(self, db: Session, room_data: dict) -> ChatRoom:
        """Create a new chat room"""
        room = ChatRoom(**room_data)
        db.add(room)
        db.commit()
        db.refresh(room)
        return room
    
    def get_by_id(self, db: Session, room_id: str) -> Optional[ChatRoom]:
        """Get chat room by ID"""
        return db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    
    def get_by_project_id(self, db: Session, project_id: str) -> Optional[ChatRoom]:
        """Get chat room by project ID"""
        return db.query(ChatRoom).filter(ChatRoom.project_id == project_id).first()
    
    def get_rooms_for_user(self, db: Session, user_id: str, org_id: str) -> List[ChatRoom]:
        """Get all chat rooms where user is a participant"""
        return db.query(ChatRoom).join(
            ChatRoomParticipant, ChatRoom.id == ChatRoomParticipant.room_id
        ).filter(
            and_(
                ChatRoomParticipant.user_id == user_id,
                ChatRoom.org_id == org_id
            )
        ).order_by(desc(ChatRoom.updated_at)).all()
    
    def update(self, db: Session, room_id: str, update_data: dict) -> Optional[ChatRoom]:
        """Update chat room"""
        room = self.get_by_id(db, room_id)
        if room:
            for key, value in update_data.items():
                setattr(room, key, value)
            room.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(room)
        return room
    
    def delete(self, db: Session, room_id: str) -> bool:
        """Delete chat room"""
        room = self.get_by_id(db, room_id)
        if room:
            db.delete(room)
            db.commit()
            return True
        return False


class ChatRoomParticipantRepository:
    """Repository for ChatRoomParticipant operations"""
    
    def add_participant(self, db: Session, participant_data: dict) -> ChatRoomParticipant:
        """Add participant to chat room"""
        participant = ChatRoomParticipant(**participant_data)
        db.add(participant)
        db.commit()
        db.refresh(participant)
        return participant
    
    def get_participants(self, db: Session, room_id: str) -> List[ChatRoomParticipant]:
        """Get all participants in a chat room"""
        return db.query(ChatRoomParticipant).filter(
            ChatRoomParticipant.room_id == room_id
        ).all()
    
    def get_participant(self, db: Session, room_id: str, user_id: str) -> Optional[ChatRoomParticipant]:
        """Get specific participant in a chat room"""
        return db.query(ChatRoomParticipant).filter(
            and_(
                ChatRoomParticipant.room_id == room_id,
                ChatRoomParticipant.user_id == user_id
            )
        ).first()
    
    def is_participant(self, db: Session, room_id: str, user_id: str) -> bool:
        """Check if user is participant in chat room"""
        return self.get_participant(db, room_id, user_id) is not None
    
    def remove_participant(self, db: Session, room_id: str, user_id: str) -> bool:
        """Remove participant from chat room"""
        participant = self.get_participant(db, room_id, user_id)
        if participant:
            db.delete(participant)
            db.commit()
            return True
        return False
    
    def update_last_read(self, db: Session, room_id: str, user_id: str) -> bool:
        """Update last read timestamp for participant"""
        participant = self.get_participant(db, room_id, user_id)
        if participant:
            participant.last_read_at = datetime.now(timezone.utc)
            db.commit()
            return True
        return False


class ChatMessageRepository:
    """Repository for ChatMessage operations"""
    
    def create(self, db: Session, message_data: dict) -> ChatMessage:
        """Create a new chat message"""
        message = ChatMessage(**message_data)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    def get_by_id(self, db: Session, message_id: str) -> Optional[ChatMessage]:
        """Get message by ID"""
        return db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    
    def get_room_messages(
        self, 
        db: Session, 
        room_id: str, 
        limit: int = 50, 
        offset: int = 0,
        before_timestamp: Optional[datetime] = None
    ) -> List[ChatMessage]:
        """Get messages in a chat room with pagination"""
        query = db.query(ChatMessage).filter(
            and_(
                ChatMessage.room_id == room_id,
                ChatMessage.is_deleted == False
            )
        )
        
        if before_timestamp:
            query = query.filter(ChatMessage.created_at < before_timestamp)
        
        return query.order_by(desc(ChatMessage.created_at)).limit(limit).offset(offset).all()
    
    def get_direct_messages(
        self, 
        db: Session, 
        user1_id: str, 
        user2_id: str, 
        limit: int = 50, 
        offset: int = 0,
        before_timestamp: Optional[datetime] = None
    ) -> List[ChatMessage]:
        """Get direct messages between two users"""
        query = db.query(ChatMessage).filter(
            and_(
                ChatMessage.room_id == None,
                or_(
                    and_(
                        ChatMessage.sender_id == user1_id,
                        ChatMessage.recipient_id == user2_id
                    ),
                    and_(
                        ChatMessage.sender_id == user2_id,
                        ChatMessage.recipient_id == user1_id
                    )
                ),
                ChatMessage.is_deleted == False
            )
        )
        
        if before_timestamp:
            query = query.filter(ChatMessage.created_at < before_timestamp)
        
        return query.order_by(desc(ChatMessage.created_at)).limit(limit).offset(offset).all()
    
    def update(self, db: Session, message_id: str, update_data: dict) -> Optional[ChatMessage]:
        """Update chat message"""
        message = self.get_by_id(db, message_id)
        if message:
            for key, value in update_data.items():
                setattr(message, key, value)
            message.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(message)
        return message
    
    def soft_delete(self, db: Session, message_id: str, delete_for_everyone: bool = False) -> bool:
        """Soft delete a message"""
        message = self.get_by_id(db, message_id)
        if message:
            message.is_deleted = True
            message.deleted_at = datetime.now(timezone.utc)
            message.deleted_for_everyone = delete_for_everyone
            db.commit()
            return True
        return False
    
    def search_messages(
        self, 
        db: Session, 
        room_id: Optional[str], 
        user_id: str,
        search_query: str,
        limit: int = 50
    ) -> List[ChatMessage]:
        """Search messages by keyword"""
        query = db.query(ChatMessage).filter(
            and_(
                ChatMessage.is_deleted == False,
                ChatMessage.message.ilike(f"%{search_query}%")
            )
        )
        
        if room_id:
            query = query.filter(ChatMessage.room_id == room_id)
        else:
            query = query.filter(
                and_(
                    ChatMessage.room_id == None,
                    or_(
                        ChatMessage.sender_id == user_id,
                        ChatMessage.recipient_id == user_id
                    )
                )
            )
        
        return query.order_by(desc(ChatMessage.created_at)).limit(limit).all()
    
    def get_unread_count(self, db: Session, room_id: str, user_id: str, last_read_at: Optional[datetime]) -> int:
        """Get count of unread messages in a room"""
        if not last_read_at:
            return db.query(ChatMessage).filter(
                and_(
                    ChatMessage.room_id == room_id,
                    ChatMessage.sender_id != user_id,
                    ChatMessage.is_deleted == False
                )
            ).count()
        
        return db.query(ChatMessage).filter(
            and_(
                ChatMessage.room_id == room_id,
                ChatMessage.sender_id != user_id,
                ChatMessage.created_at > last_read_at,
                ChatMessage.is_deleted == False
            )
        ).count()


class MessageReadReceiptRepository:
    """Repository for MessageReadReceipt operations"""
    
    def create(self, db: Session, receipt_data: dict) -> MessageReadReceipt:
        """Create a read receipt"""
        receipt = MessageReadReceipt(**receipt_data)
        db.add(receipt)
        db.commit()
        db.refresh(receipt)
        return receipt
    
    def get_receipts_for_message(self, db: Session, message_id: str) -> List[MessageReadReceipt]:
        """Get all read receipts for a message"""
        return db.query(MessageReadReceipt).filter(
            MessageReadReceipt.message_id == message_id
        ).all()
    
    def get_receipt(self, db: Session, message_id: str, user_id: str) -> Optional[MessageReadReceipt]:
        """Get specific read receipt"""
        return db.query(MessageReadReceipt).filter(
            and_(
                MessageReadReceipt.message_id == message_id,
                MessageReadReceipt.user_id == user_id
            )
        ).first()
    
    def mark_as_delivered(self, db: Session, message_id: str, user_id: str) -> bool:
        """Mark message as delivered"""
        receipt = self.get_receipt(db, message_id, user_id)
        if not receipt:
            receipt = MessageReadReceipt(
                id=f"receipt_{message_id}_{user_id}",
                message_id=message_id,
                user_id=user_id,
                delivered_at=datetime.now(timezone.utc)
            )
            db.add(receipt)
        else:
            receipt.delivered_at = datetime.now(timezone.utc)
        db.commit()
        return True
    
    def mark_as_read(self, db: Session, message_id: str, user_id: str) -> bool:
        """Mark message as read"""
        receipt = self.get_receipt(db, message_id, user_id)
        if not receipt:
            receipt = MessageReadReceipt(
                id=f"receipt_{message_id}_{user_id}",
                message_id=message_id,
                user_id=user_id,
                delivered_at=datetime.now(timezone.utc),
                read_at=datetime.now(timezone.utc)
            )
            db.add(receipt)
        else:
            receipt.read_at = datetime.now(timezone.utc)
        db.commit()
        return True


class TypingStatusRepository:
    """Repository for TypingStatus operations"""
    
    def set_typing(self, db: Session, typing_data: dict) -> TypingStatus:
        """Set typing status"""
        existing = db.query(TypingStatus).filter(
            and_(
                TypingStatus.user_id == typing_data.get("user_id"),
                TypingStatus.room_id == typing_data.get("room_id") if typing_data.get("room_id") else True,
                TypingStatus.recipient_id == typing_data.get("recipient_id") if typing_data.get("recipient_id") else True
            )
        ).first()
        
        if existing:
            existing.is_typing = typing_data.get("is_typing", True)
            existing.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            status = TypingStatus(**typing_data)
            db.add(status)
            db.commit()
            db.refresh(status)
            return status
    
    def get_typing_users(self, db: Session, room_id: Optional[str] = None, recipient_id: Optional[str] = None) -> List[TypingStatus]:
        """Get users currently typing"""
        query = db.query(TypingStatus).filter(TypingStatus.is_typing == True)
        
        if room_id:
            query = query.filter(TypingStatus.room_id == room_id)
        elif recipient_id:
            query = query.filter(TypingStatus.recipient_id == recipient_id)
        
        return query.all()
    
    def clear_typing(self, db: Session, user_id: str, room_id: Optional[str] = None, recipient_id: Optional[str] = None) -> bool:
        """Clear typing status"""
        query = db.query(TypingStatus).filter(TypingStatus.user_id == user_id)
        
        if room_id:
            query = query.filter(TypingStatus.room_id == room_id)
        elif recipient_id:
            query = query.filter(TypingStatus.recipient_id == recipient_id)
        
        status = query.first()
        if status:
            status.is_typing = False
            status.updated_at = datetime.now(timezone.utc)
            db.commit()
            return True
        return False


class ChatNotificationSettingsRepository:
    """Repository for ChatNotificationSettings operations"""
    
    def create(self, db: Session, settings_data: dict) -> ChatNotificationSettings:
        """Create notification settings"""
        settings = ChatNotificationSettings(**settings_data)
        db.add(settings)
        db.commit()
        db.refresh(settings)
        return settings
    
    def get_by_user_id(self, db: Session, user_id: str) -> Optional[ChatNotificationSettings]:
        """Get notification settings for user"""
        return db.query(ChatNotificationSettings).filter(
            ChatNotificationSettings.user_id == user_id
        ).first()
    
    def get_or_create(self, db: Session, user_id: str) -> ChatNotificationSettings:
        """Get or create notification settings for user"""
        settings = self.get_by_user_id(db, user_id)
        if not settings:
            settings = self.create(db, {
                "id": f"settings_{user_id}",
                "user_id": user_id
            })
        return settings
    
    def update(self, db: Session, user_id: str, update_data: dict) -> Optional[ChatNotificationSettings]:
        """Update notification settings"""
        settings = self.get_by_user_id(db, user_id)
        if settings:
            for key, value in update_data.items():
                setattr(settings, key, value)
            settings.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(settings)
        return settings
