__all__ = (
    "router",
)

from aiogram import Router

from .base_callbacks import router as base_callbacks_router

router = Router(name=__name__)

router.include_router(base_callbacks_router)
