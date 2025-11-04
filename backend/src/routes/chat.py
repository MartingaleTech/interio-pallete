"""
Chat API Routes
Handles REST API and WebSocket endpoints for chat functionality
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import json
import logging
from datetime import datetime

from src.config.database import get_db
from src.dependencies.auth_new import get_current_user, get_current_user_ws
from src.services.chat_service import ChatService
from src.services.websocket_manager import connection_manager
from src.database.models import User
from src.models.chat import (
    CreateChatRoomRequest,
    SendMessageRequest,
    SendDirectMessageRequest,
    EditMessageRequest,
    AddParticipantRequest,
    UpdateNotificationSettingsRequest,
    TypingStatusRequest,
    SearchMessagesRequest,
    ChatRoomResponse,
    ChatMessageResponse,
    MessageHistoryResponse,
    UnreadCountResponse,
    ChatNotificationSettingsResponse,
    WSMessageType
)

logger = logging.getLogger(__name__)

router = APIRouter()
chat_service = ChatService()


@router.websocket("/ws/chat")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time chat"""
    try:
        logger.info(f"[WS] Connection attempt - token present: {bool(token)}, token length: {len(token) if token else 0}")
        user = await get_current_user_ws(token, db)
        if not user:
            logger.error(f"[WS] Authentication failed - token: {token[:20]}...")
            await websocket.close(code=1008, reason="Authentication failed")
            return
        
        logger.info(f"[WS] User authenticated: {user.id} ({user.email})")
        await connection_manager.connect(websocket, user.id)
        
        try:
            while True:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                message_type = message_data.get("type")
                payload = message_data.get("data", {})
                
                if message_type == WSMessageType.SEND_MESSAGE:
                    await handle_send_message(db, user, payload)
                
                elif message_type == WSMessageType.EDIT_MESSAGE:
                    await handle_edit_message(db, user, payload)
                
                elif message_type == WSMessageType.DELETE_MESSAGE:
                    await handle_delete_message(db, user, payload)
                
                elif message_type == WSMessageType.TYPING_START:
                    await handle_typing_start(db, user, payload)
                
                elif message_type == WSMessageType.TYPING_STOP:
                    await handle_typing_stop(db, user, payload)
                
                elif message_type == WSMessageType.MARK_READ:
                    await handle_mark_read(db, user, payload)
                
                elif message_type == WSMessageType.JOIN_ROOM:
                    await handle_join_room(db, user, payload)
                
                elif message_type == WSMessageType.LEAVE_ROOM:
                    await handle_leave_room(db, user, payload)
                
                else:
                    await connection_manager.send_error(
                        user.id,
                        f"Unknown message type: {message_type}"
                    )
        
        except WebSocketDisconnect:
            await connection_manager.disconnect(websocket)
        
        except Exception as e:
            logger.error(f"WebSocket error for user {user.id}: {e}")
            await connection_manager.send_error(user.id, "Internal server error", str(e))
            await connection_manager.disconnect(websocket)
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        await websocket.close(code=1011, reason="Internal server error")


async def handle_send_message(db: Session, user: User, payload: dict):
    """Handle sending a message"""
    try:
        room_id = payload.get("room_id")
        recipient_id = payload.get("recipient_id")
        
        if room_id:
            request = SendMessageRequest(**payload)
            message = chat_service.send_message(db, user, room_id, request)
            
            await connection_manager.broadcast_to_room(
                room_id,
                {
                    "type": WSMessageType.NEW_MESSAGE,
                    "data": {
                        "id": message.id,
                        "room_id": message.room_id,
                        "sender_id": message.sender_id,
                        "sender_name": message.sender_name,
                        "message": message.message,
                        "message_type": message.message_type,
                        "attachment_url": message.attachment_url,
                        "attachment_name": message.attachment_name,
                        "attachment_type": message.attachment_type,
                        "attachment_size": message.attachment_size,
                        "parent_message_id": message.parent_message_id,
                        "mentions": message.mentions,
                        "created_at": message.created_at.isoformat(),
                        "updated_at": message.updated_at.isoformat()
                    }
                }
            )
        
        elif recipient_id:
            request = SendDirectMessageRequest(**payload)
            message = chat_service.send_direct_message(db, user, request)
            
            await connection_manager.send_direct_message_notification(
                user.id,
                recipient_id,
                {
                    "type": WSMessageType.NEW_MESSAGE,
                    "data": {
                        "id": message.id,
                        "sender_id": message.sender_id,
                        "sender_name": message.sender_name,
                        "recipient_id": message.recipient_id,
                        "message": message.message,
                        "message_type": message.message_type,
                        "attachment_url": message.attachment_url,
                        "attachment_name": message.attachment_name,
                        "attachment_type": message.attachment_type,
                        "attachment_size": message.attachment_size,
                        "created_at": message.created_at.isoformat(),
                        "updated_at": message.updated_at.isoformat()
                    }
                }
            )
            
            await connection_manager.send_personal_message(
                user.id,
                {
                    "type": WSMessageType.NEW_MESSAGE,
                    "data": {
                        "id": message.id,
                        "sender_id": message.sender_id,
                        "sender_name": message.sender_name,
                        "recipient_id": message.recipient_id,
                        "message": message.message,
                        "message_type": message.message_type,
                        "created_at": message.created_at.isoformat()
                    }
                }
            )
    
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        await connection_manager.send_error(user.id, "Failed to send message", str(e))


async def handle_edit_message(db: Session, user: User, payload: dict):
    """Handle editing a message"""
    try:
        message_id = payload.get("message_id")
        request = EditMessageRequest(message=payload.get("message"))
        
        message = chat_service.edit_message(db, user, message_id, request)
        
        edit_data = {
            "type": WSMessageType.MESSAGE_EDITED,
            "data": {
                "message_id": message.id,
                "message": message.message,
                "is_edited": True,
                "edited_at": message.edited_at.isoformat()
            }
        }
        
        if message.room_id:
            await connection_manager.broadcast_to_room(message.room_id, edit_data)
        elif message.recipient_id:
            await connection_manager.send_personal_message(message.recipient_id, edit_data)
            await connection_manager.send_personal_message(user.id, edit_data)
    
    except Exception as e:
        logger.error(f"Error editing message: {e}")
        await connection_manager.send_error(user.id, "Failed to edit message", str(e))


async def handle_delete_message(db: Session, user: User, payload: dict):
    """Handle deleting a message"""
    try:
        message_id = payload.get("message_id")
        delete_for_everyone = payload.get("delete_for_everyone", False)
        
        from src.repositories.chat_repository import ChatMessageRepository
        message_repo = ChatMessageRepository()
        message = message_repo.get_by_id(db, message_id)
        
        if not message:
            raise ValueError("Message not found")
        
        chat_service.delete_message(db, user, message_id, delete_for_everyone)
        
        delete_data = {
            "type": WSMessageType.MESSAGE_DELETED,
            "data": {
                "message_id": message_id,
                "deleted_for_everyone": delete_for_everyone
            }
        }
        
        if message.room_id:
            if delete_for_everyone:
                await connection_manager.broadcast_to_room(message.room_id, delete_data)
            else:
                await connection_manager.send_personal_message(user.id, delete_data)
        elif message.recipient_id:
            if delete_for_everyone:
                await connection_manager.send_personal_message(message.recipient_id, delete_data)
            await connection_manager.send_personal_message(user.id, delete_data)
    
    except Exception as e:
        logger.error(f"Error deleting message: {e}")
        await connection_manager.send_error(user.id, "Failed to delete message", str(e))


async def handle_typing_start(db: Session, user: User, payload: dict):
    """Handle typing start event"""
    try:
        room_id = payload.get("room_id")
        recipient_id = payload.get("recipient_id")
        
        request = TypingStatusRequest(
            is_typing=True,
            room_id=room_id,
            recipient_id=recipient_id
        )
        
        chat_service.set_typing_status(db, user, request)
        
        await connection_manager.broadcast_typing_status(
            user.id, room_id, recipient_id, True
        )
    
    except Exception as e:
        logger.error(f"Error handling typing start: {e}")


async def handle_typing_stop(db: Session, user: User, payload: dict):
    """Handle typing stop event"""
    try:
        room_id = payload.get("room_id")
        recipient_id = payload.get("recipient_id")
        
        request = TypingStatusRequest(
            is_typing=False,
            room_id=room_id,
            recipient_id=recipient_id
        )
        
        chat_service.set_typing_status(db, user, request)
        
        await connection_manager.broadcast_typing_status(
            user.id, room_id, recipient_id, False
        )
    
    except Exception as e:
        logger.error(f"Error handling typing stop: {e}")


async def handle_mark_read(db: Session, user: User, payload: dict):
    """Handle marking messages as read"""
    try:
        message_ids = payload.get("message_ids", [])
        room_id = payload.get("room_id")
        
        chat_service.mark_messages_as_read(db, user, room_id, message_ids)
        
        from src.repositories.chat_repository import ChatMessageRepository
        message_repo = ChatMessageRepository()
        
        for message_id in message_ids:
            message = message_repo.get_by_id(db, message_id)
            if message and message.sender_id != user.id:
                await connection_manager.broadcast_message_read(
                    message_id, user.id, room_id, message.sender_id
                )
    
    except Exception as e:
        logger.error(f"Error marking messages as read: {e}")


async def handle_join_room(db: Session, user: User, payload: dict):
    """Handle joining a chat room"""
    try:
        room_id = payload.get("room_id")
        
        room = chat_service.get_chat_room(db, user, room_id)
        if room:
            await connection_manager.join_room(user.id, room_id)
    
    except Exception as e:
        logger.error(f"Error joining room: {e}")
        await connection_manager.send_error(user.id, "Failed to join room", str(e))


async def handle_leave_room(db: Session, user: User, payload: dict):
    """Handle leaving a chat room"""
    try:
        room_id = payload.get("room_id")
        await connection_manager.leave_room(user.id, room_id)
    
    except Exception as e:
        logger.error(f"Error leaving room: {e}")



@router.post("/api/v1/chat/rooms", response_model=ChatRoomResponse)
def create_chat_room(
    request: CreateChatRoomRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create a new chat room for a project"""
    try:
        room = chat_service.create_chat_room(db, user, request)
        return room
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating chat room: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/api/v1/chat/rooms", response_model=List[ChatRoomResponse])
def get_user_chat_rooms(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all chat rooms for the current user"""
    try:
        logger.info(f"Getting chat rooms for user type: {type(user)}, user: {user}")
        rooms = chat_service.get_user_chat_rooms(db, user)
        return rooms
    except Exception as e:
        logger.exception(f"Error getting chat rooms: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/api/v1/chat/rooms/{room_id}", response_model=ChatRoomResponse)
def get_chat_room(
    room_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get a specific chat room"""
    try:
        room = chat_service.get_chat_room(db, user, room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Chat room not found")
        return room
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting chat room: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/api/v1/chat/rooms/{room_id}/participants")
def add_participant(
    room_id: str,
    request: AddParticipantRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Add a participant to a chat room"""
    try:
        chat_service.add_participant_to_room(db, room_id, request.user_id, request.is_admin)
        return {"message": "Participant added successfully"}
    except Exception as e:
        logger.error(f"Error adding participant: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/api/v1/chat/rooms/{room_id}/participants/{user_id}")
def remove_participant(
    room_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Remove a participant from a chat room"""
    try:
        chat_service.remove_participant_from_room(db, user, room_id, user_id)
        return {"message": "Participant removed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error removing participant: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/api/v1/chat/rooms/{room_id}/participants")
def get_room_participants(
    room_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all participants in a chat room"""
    try:
        participants = chat_service.get_room_participants(db, user, room_id)
        return participants
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting participants: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/api/v1/chat/rooms/{room_id}/messages")
def get_room_messages(
    room_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    before: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get messages in a chat room with pagination"""
    try:
        before_timestamp = datetime.fromisoformat(before) if before else None
        result = chat_service.get_room_messages(db, user, room_id, limit, offset, before_timestamp)
        return result
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting room messages: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/api/v1/chat/direct/{user_id}/messages")
def get_direct_messages(
    user_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    before: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get direct messages with another user"""
    try:
        before_timestamp = datetime.fromisoformat(before) if before else None
        result = chat_service.get_direct_messages(db, user, user_id, limit, offset, before_timestamp)
        return result
    except Exception as e:
        logger.error(f"Error getting direct messages: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/api/v1/chat/direct/conversations")
def get_direct_conversations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get list of direct message conversations"""
    try:
        logger.info(f"Getting direct conversations for user type: {type(user)}, user: {user}")
        conversations = chat_service.get_direct_message_conversations(db, user)
        return conversations
    except Exception as e:
        logger.exception(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/api/v1/chat/org/members")
def get_org_members(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all members in the user's organization for direct messaging"""
    try:
        from src.repositories.user_repository import UserRepository
        user_repo = UserRepository(db)
        
        members = db.query(User).filter(
            User.org_id == user.org_id,
            User.id != user.id
        ).all()
        
        return [{
            "id": member.id,
            "name": member.name,
            "email": member.email,
            "role": member.role.value if hasattr(member.role, 'value') else member.role
        } for member in members]
    except Exception as e:
        logger.error(f"Error getting org members: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/api/v1/chat/search")
def search_messages(
    request: SearchMessagesRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Search messages by keyword"""
    try:
        messages = chat_service.search_messages(db, user, request)
        return {"messages": messages}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/api/v1/chat/rooms/{room_id}/unread")
def get_unread_count(
    room_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get unread message count for a room"""
    try:
        count = chat_service.get_unread_count(db, user, room_id)
        return {"room_id": room_id, "unread_count": count}
    except Exception as e:
        logger.error(f"Error getting unread count: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/api/chat/settings", response_model=ChatNotificationSettingsResponse)
def get_notification_settings(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get notification settings for current user"""
    try:
        settings = chat_service.get_notification_settings(db, user)
        return settings
    except Exception as e:
        logger.error(f"Error getting notification settings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/api/chat/settings", response_model=ChatNotificationSettingsResponse)
def update_notification_settings(
    request: UpdateNotificationSettingsRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update notification settings for current user"""
    try:
        settings = chat_service.update_notification_settings(db, user, request)
        return settings
    except Exception as e:
        logger.error(f"Error updating notification settings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
