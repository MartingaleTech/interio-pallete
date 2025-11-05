"""
WebSocket Manager for Real-Time Chat
Handles WebSocket connections, message broadcasting, and connection management
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Optional, List
import json
import asyncio
from datetime import datetime
import logging

from src.models.chat import WSMessage, WSMessageType, WSErrorMessage

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for chat"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
        self.room_subscriptions: Dict[str, Set[str]] = {}
        
        self.user_rooms: Dict[str, Set[str]] = {}
        
        self.dm_subscriptions: Dict[str, Set[str]] = {}
        
        self.connection_metadata: Dict[WebSocket, str] = {}
        
        self.lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        
        async with self.lock:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            
            self.active_connections[user_id].add(websocket)
            self.connection_metadata[websocket] = user_id
            
            logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")
        
        await self.send_personal_message(
            user_id,
            {
                "type": WSMessageType.CONNECTED,
                "data": {
                    "user_id": user_id,
                    "timestamp": datetime.now(datetime.UTC).isoformat()
                }
            }
        )
    
    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        async with self.lock:
            user_id = self.connection_metadata.get(websocket)
            
            if user_id and user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                    
                    if user_id in self.user_rooms:
                        for room_id in self.user_rooms[user_id]:
                            if room_id in self.room_subscriptions:
                                self.room_subscriptions[room_id].discard(user_id)
                                if not self.room_subscriptions[room_id]:
                                    del self.room_subscriptions[room_id]
                        del self.user_rooms[user_id]
                    
                    if user_id in self.dm_subscriptions:
                        del self.dm_subscriptions[user_id]
                
                if websocket in self.connection_metadata:
                    del self.connection_metadata[websocket]
                
                logger.info(f"User {user_id} disconnected")
    
    async def join_room(self, user_id: str, room_id: str):
        """Subscribe user to a chat room"""
        async with self.lock:
            if room_id not in self.room_subscriptions:
                self.room_subscriptions[room_id] = set()
            
            self.room_subscriptions[room_id].add(user_id)
            
            if user_id not in self.user_rooms:
                self.user_rooms[user_id] = set()
            
            self.user_rooms[user_id].add(room_id)
            
            logger.info(f"User {user_id} joined room {room_id}")
        
        await self.broadcast_to_room(
            room_id,
            {
                "type": WSMessageType.USER_JOINED,
                "data": {
                    "user_id": user_id,
                    "room_id": room_id,
                    "timestamp": datetime.now(datetime.UTC).isoformat()
                }
            },
            exclude_user=user_id
        )
    
    async def leave_room(self, user_id: str, room_id: str):
        """Unsubscribe user from a chat room"""
        async with self.lock:
            if room_id in self.room_subscriptions:
                self.room_subscriptions[room_id].discard(user_id)
                
                if not self.room_subscriptions[room_id]:
                    del self.room_subscriptions[room_id]
            
            if user_id in self.user_rooms:
                self.user_rooms[user_id].discard(room_id)
                
                if not self.user_rooms[user_id]:
                    del self.user_rooms[user_id]
            
            logger.info(f"User {user_id} left room {room_id}")
        
        await self.broadcast_to_room(
            room_id,
            {
                "type": WSMessageType.USER_LEFT,
                "data": {
                    "user_id": user_id,
                    "room_id": room_id,
                    "timestamp": datetime.now(datetime.UTC).isoformat()
                }
            }
        )
    
    async def send_personal_message(self, user_id: str, message: dict):
        """Send message to all connections of a specific user"""
        if user_id not in self.active_connections:
            return
        
        connections = list(self.active_connections[user_id])
        
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                await self.disconnect(connection)
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude_user: Optional[str] = None):
        """Broadcast message to all users in a room"""
        if room_id not in self.room_subscriptions:
            return
        
        user_ids = list(self.room_subscriptions[room_id])
        
        for user_id in user_ids:
            if exclude_user and user_id == exclude_user:
                continue
            
            await self.send_personal_message(user_id, message)
    
    async def send_direct_message_notification(self, sender_id: str, recipient_id: str, message: dict):
        """Send direct message to recipient"""
        await self.send_personal_message(recipient_id, message)
    
    async def broadcast_typing_status(self, user_id: str, room_id: Optional[str], recipient_id: Optional[str], is_typing: bool):
        """Broadcast typing status to room or DM recipient"""
        message = {
            "type": WSMessageType.USER_TYPING if is_typing else WSMessageType.USER_STOPPED_TYPING,
            "data": {
                "user_id": user_id,
                "room_id": room_id,
                "recipient_id": recipient_id,
                "timestamp": datetime.now(datetime.UTC).isoformat()
            }
        }
        
        if room_id:
            await self.broadcast_to_room(room_id, message, exclude_user=user_id)
        elif recipient_id:
            await self.send_personal_message(recipient_id, message)
    
    async def broadcast_message_read(self, message_id: str, user_id: str, room_id: Optional[str], sender_id: str):
        """Broadcast message read receipt"""
        message = {
            "type": WSMessageType.MESSAGE_READ,
            "data": {
                "message_id": message_id,
                "user_id": user_id,
                "room_id": room_id,
                "timestamp": datetime.now(datetime.UTC).isoformat()
            }
        }
        
        await self.send_personal_message(sender_id, message)
    
    async def broadcast_message_delivered(self, message_id: str, user_id: str, sender_id: str):
        """Broadcast message delivered receipt"""
        message = {
            "type": WSMessageType.MESSAGE_DELIVERED,
            "data": {
                "message_id": message_id,
                "user_id": user_id,
                "timestamp": datetime.now(datetime.UTC).isoformat()
            }
        }
        
        await self.send_personal_message(sender_id, message)
    
    async def send_error(self, user_id: str, error: str, details: Optional[str] = None):
        """Send error message to user"""
        message = {
            "type": WSMessageType.ERROR,
            "error": error,
            "details": details,
            "timestamp": datetime.now(datetime.UTC).isoformat()
        }
        
        await self.send_personal_message(user_id, message)
    
    def get_active_users(self) -> List[str]:
        """Get list of all active user IDs"""
        return list(self.active_connections.keys())
    
    def get_room_users(self, room_id: str) -> List[str]:
        """Get list of user IDs in a room"""
        if room_id in self.room_subscriptions:
            return list(self.room_subscriptions[room_id])
        return []
    
    def is_user_online(self, user_id: str) -> bool:
        """Check if user has any active connections"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0
    
    def get_connection_count(self, user_id: str) -> int:
        """Get number of active connections for a user"""
        if user_id in self.active_connections:
            return len(self.active_connections[user_id])
        return 0


connection_manager = ConnectionManager()
