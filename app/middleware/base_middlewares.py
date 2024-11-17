import logging
from typing import Callable, Awaitable, Any, Dict

from aiogram import BaseMiddleware
from aiogram.enums import ChatMemberStatus
from aiogram.types import Message, TelegramObject, ChatMemberLeft, CallbackQuery, ChatMember
from aiogram.fsm.storage.redis import RedisStorage



# class LogMiddleware(BaseMiddleware):
#
#     async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data: Dict[str, Any]) -> Any:
#         result = await handler(event, data)
#         return result



class ChannelHandlerMiddleware(BaseMiddleware):
    def __init__(self, storage: RedisStorage):
        self.storage = storage

    async def __call__(self,
                       handler: Callable[[ChatMember, Dict[str, Any]], Awaitable[Any]],
                       event: ChatMember,
                       data: Dict[str, Any]) -> Any:
        user = f'user_{event.from_user.id}'

        logging.debug(f"MIDDLEWARE - {self.__class__.__name__}: {user} - {event.new_chat_member.status}")
        match event.new_chat_member.status:
            case ChatMemberStatus.MEMBER:
                await self.storage.redis.set(name=user, value=1)
            case ChatMemberStatus.LEFT:
                await self.storage.redis.delete(user)
        return await handler(event, data)
