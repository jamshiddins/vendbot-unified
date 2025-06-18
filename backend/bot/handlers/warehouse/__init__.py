from aiogram import Router
from .receiving import router as receiving_router
from .issue import router as issue_router
from .inventory import router as inventory_router

router = Router(name="warehouse")

router.include_router(receiving_router)
router.include_router(issue_router)
router.include_router(inventory_router)