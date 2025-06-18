from fastapi import WebSocket, WebSocketDisconnect, Depends, Query
from typing import Dict, Set
import json
import asyncio
from datetime import datetime
from core.config import settings
from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from core.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Хранилище активных соединений по ролям
        self.active_connections: Dict[str, Set[WebSocket]] = {
            'admin': set(),
            'warehouse': set(),
            'operator': set(),
            'driver': set(),
            'all': set()  # Для broadcast всем
        }
        self.user_connections: Dict[int, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int, role: str):
        """Подключение пользователя"""
        await websocket.accept()
        self.active_connections[role].add(websocket)
        self.active_connections['all'].add(websocket)
        self.user_connections[user_id] = websocket
        
        # Отправляем приветственное сообщение
        await websocket.send_json({
            'type': 'connection',
            'status': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        logger.info(f"User {user_id} ({role}) connected via WebSocket")
    
    def disconnect(self, websocket: WebSocket, user_id: int, role: str):
        """Отключение пользователя"""
        self.active_connections[role].discard(websocket)
        self.active_connections['all'].discard(websocket)
        self.user_connections.pop(user_id, None)
        
        logger.info(f"User {user_id} ({role}) disconnected from WebSocket")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Отправка сообщения конкретному пользователю"""
        websocket = self.user_connections.get(user_id)
        if websocket:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
    
    async def broadcast_to_role(self, message: dict, role: str):
        """Отправка сообщения всем пользователям роли"""
        dead_connections = set()
        
        for connection in self.active_connections[role]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to role {role}: {e}")
                dead_connections.add(connection)
        
        # Удаляем мертвые соединения
        for connection in dead_connections:
            self.active_connections[role].discard(connection)
    
    async def broadcast_operation(self, operation_data: dict, source_channel: str):
        """Broadcast операции всем подключенным клиентам"""
        message = {
            'type': 'operation_update',
            'operation': operation_data,
            'source_channel': source_channel,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Отправляем всем
        await self.broadcast_to_role(message, 'all')
        
        # Обновляем sync_status
        operation_data['sync_status']['web'] = True
    
    async def broadcast_inventory_update(self, inventory_data: dict):
        """Broadcast обновления инвентаря"""
        message = {
            'type': 'inventory_update',
            'data': inventory_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Отправляем складу и админам
        await self.broadcast_to_role(message, 'warehouse')
        await self.broadcast_to_role(message, 'admin')

# Глобальный менеджер соединений
ws_manager = ConnectionManager()