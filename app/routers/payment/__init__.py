__all__ = (
    "router",
)

from aiogram import Router

from .base_payment import router as payment_router

router = Router(name=__name__)

router.include_router(payment_router)
