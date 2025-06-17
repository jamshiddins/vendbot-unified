# backend/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await init_redis()
    await init_telegram_bot()
    yield
    # Shutdown
    await close_connections()

app = FastAPI(
    title="VendBot API",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Единые эндпоинты для всех каналов
@app.post("/api/v2/assets")
async def create_asset(asset: AssetCreate, channel: str = Header()):
    """Создание актива из любого канала (telegram/web/mobile)"""
    result = await asset_service.create(asset)
    await sync_service.broadcast(result, channel)
    return result

@app.post("/api/v2/hopper-operations")
async def hopper_operation(operation: HopperOperationCreate, channel: str = Header()):
    """Операция с бункером с автоматической синхронизацией"""
    result = await hopper_service.process_operation(operation)
    await sync_service.broadcast(result, channel)
    return result

@app.get("/api/v2/analytics/consumption")
async def get_consumption_analysis(machine_id: int, period: str):
    """Анализ расхода vs продажи"""
    return await analytics_service.analyze_consumption(machine_id, period)