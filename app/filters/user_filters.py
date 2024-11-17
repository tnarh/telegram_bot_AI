import datetime
import logging

from aiogram.filters import Filter
from aiogram.types import Message
from aiogram.fsm.storage.redis import RedisStorage

from config import ADMIN_LIST, REDIS_URL
from app.database.requests import db


storage = RedisStorage.from_url(REDIS_URL)
logger = logging.getLogger(__name__)


class Subscribe(Filter):
    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id

        user_data = await db.get_user_data(user_id)
        used_generations = user_data.get('used_generations')
        subscription_end_date = user_data.get('subscription_end_date')

        if used_generations < 3 or user_id in ADMIN_LIST:
            return True
        if subscription_end_date is None or subscription_end_date < datetime.datetime.now():
            logging.info(f'subscription_end_date: {subscription_end_date}')
            return False
        elif user_data.get('daily_generation') > 20:
            return False
        elif subscription_end_date > datetime.datetime.now():
            return True



class Admins(Filter):
    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        if user_id in ADMIN_LIST:
            return True



class UserInDatabase(Filter):
    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        user = await storage.redis.get(name=f'user_{user_id}')
        if user:
            logger.info(f'Пользователь: {user_id} в кэш памяти')
            return True
        else:
            logger.info(f'Пользователя: {user_id} нет в кэш памяти')
            user_data = await db.get_user_data(user_id=user_id)
            if user_data:
                logger.info(f'Пользователь: {user_id} есть в БД')
                await storage.redis.set(name=f'user_{user_id}', value=1)
                return True
            else:
                logger.info(f'Пользователя: {user_id} нет в БД')
                return False



