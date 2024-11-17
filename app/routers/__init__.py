__all__ = (
    "router",
)

from aiogram import Router

from .commands import router as commands_router
from .callbacks import router as callbacks_router
from .messages import router as messages_router
from .channel import router as channels_router
from .payment import router as payments_router

router = Router(name=__name__)
router.include_routers(
    commands_router,
    callbacks_router,
    messages_router,
    channels_router,
    payments_router,
)

