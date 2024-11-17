__all__ = (
    "router",
)

from aiogram import Router

from .media_handlers import router as user_messages_router
from .text_handlers import router as text_router

router = Router(name=__name__)

router.include_routers(
    user_messages_router,
    text_router,
)
