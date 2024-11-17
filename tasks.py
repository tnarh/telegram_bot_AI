import asyncio
import logging
from datetime import datetime, timedelta

from app.database.requests import db

logger = logging.getLogger(__name__)


class TasksContainer:
    def __init__(self):
        self.tasks = []


container = TasksContainer()


async def reset_daily_generations():
    """Задача сброса ежедневных генераций
     у каждого пользователя """
    while True:
        # Вычисляем время до следующего сброса
        now = datetime.now()
        next_reset = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        seconds_until_reset = (next_reset - now).total_seconds()
        await asyncio.sleep(seconds_until_reset)
        try:
            logger.info('Сброс ежедневных генераций')
            await db.reset_daily_limit_for_all_users()
        except Exception as e:
            logger.error(f'Ошибка сброса ежедневных генераций: {e}')


# async def reset_daily_generations():
#     """Задача сброса ежедневных генераций
#      у каждого пользователя """
#     while True:
#         await asyncio.sleep(10)
#         logger.info('Сброс ежедневных генераций')
#         try:
#             await db.reset_daily_limit_for_all_users()
#         except Exception as e:
#             logger.error(f'Ошибка сброса ежедневных генераций: {e}')



async def launching_the_daily_generation_reset_task() -> None:
    """
    Запускает задачу сброса ежедневных генераций у каждого пользователя
    """
    logger.info('Запуск задачи сброса ежедневных генераций')
    task = asyncio.create_task(reset_daily_generations())
    container.tasks.append(task)
    return
