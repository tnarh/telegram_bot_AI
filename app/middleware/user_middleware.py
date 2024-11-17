import logging
from typing import Callable, Awaitable, Any, Dict

import redis
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, ChatMemberLeft, CallbackQuery
from aiogram.fsm.storage.redis import RedisStorage

from app.keyboards import subscribe
from app.localization_loader import LocalizationLoader
from config import TELEGRAM_CHANEL_ID

locales = LocalizationLoader()


class CheckUserInGroupMiddleware(BaseMiddleware):
    def __init__(self, storage: RedisStorage):
        self.storage = storage

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:

        user = f'user_{event.from_user.id}'
        logging.debug(f"MIDDLEWARE:{self.__class__.__name__}: key: {user}")

        try:
            check_user = await self.storage.redis.get(name=user)
            if check_user:
                return await handler(event, data)
            else:
                user_status = await event.bot.get_chat_member(chat_id=TELEGRAM_CHANEL_ID, user_id=event.from_user.id)
                match user_status:
                    case ChatMemberLeft():
                        if type(event) == CallbackQuery:
                            return await event.message.edit_text(locales.get_message(language=event.from_user.language_code, message_key='not_sub_message'), reply_markup=await subscribe(event.from_user.language_code))
                        return await event.answer(locales.get_message(language=event.from_user.language_code, message_key='not_sub_message'), reply_markup=await subscribe(event.from_user.language_code))
                    case _:
                        await self.storage.redis.set(name=user, value=1)
                        return await handler(event, data)
        except redis.exceptions.ConnectionError:
            logging.error('Ошибка подключения к redis')
