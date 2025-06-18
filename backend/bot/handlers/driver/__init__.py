from aiogram import Router
from .route import router as route_router
from .delivery import router as delivery_router

router = Router(name="driver")

router.include_router(route_router)
router.include_router(delivery_router)