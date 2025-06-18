from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from api.endpoints import users, assets, ingredients, operations, auth
from api.websocket import ws_manager
from core.auth import decode_token
from db.database import get_db
from core.services.user_service import UserService

api_router = APIRouter()

# Подключаем обычные REST-роуты
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(ingredients.router, prefix="/ingredients", tags=["ingredients"])
api_router.include_router(operations.router, prefix="/operations", tags=["operations"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# WebSocket endpoint
@api_router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint для real-time обновлений"""
    try:
        # Авторизация через токен
        payload = decode_token(token)
        user_id = payload.get("sub")

        # Получаем пользователя
        user_service = UserService(db)
        user = await user_service.get_user(int(user_id))

        if not user:
            await websocket.close(code=4001, reason="User not found")
            return

        # Подключаем WebSocket
        await ws_manager.connect(websocket, user.id, user.role.value)

        try:
            while True:
                data = await websocket.receive_json()
                if data.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket, user.id, user.role.value)
    except Exception as e:
        await websocket.close(code=4000, reason=str(e))