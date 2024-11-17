__all__ = (
    "router",
)

from aiogram import Router

from .channel_handler import router as channel_handlers_router

router = Router(name=__name__)

router.include_router(channel_handlers_router)
