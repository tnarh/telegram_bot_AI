import asyncio
import logging
from typing import Dict, Sequence

import sqlalchemy
from aiogram.types import Message
from sqlalchemy import select, DateTime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import DATABASE
from app.database.models import UsersORM, Base, PaymentsORM


class Database:

    def __init__(self):
        self.__async_engine = create_async_engine(
            url=DATABASE,
            # echo=True,
        )
        self.__async_session_factory = async_sessionmaker(self.__async_engine)
        asyncio.run(self._init_models())

    async def _init_models(self) -> None:
        """
        Создает базу данных с таблицами
        :return:
        """
        async with self.__async_engine.begin() as conn:
            # await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    async def add_user(self, user_id: int, name, username) -> None:
        """
        Добавляет пользователя в БД с определенным количеством генераций
        :param user_id: ID пользователя
        :param name: Имя пользователя
        :param username: Никнейм пользователя
        :return: None
        """

        try:
            async with self.__async_session_factory() as session:
                user = UsersORM(
                    id=user_id,
                    name=name,
                    username=username,
                    used_generations=0
                )
                session.add(user)
                # session.add_all([user, ])
                await session.commit()
        except sqlalchemy.exc.IntegrityError:
            logging.error('Уже есть пользователь в Базе Данных')
        except sqlalchemy.exc.OperationalError:
            logging.error('Базы Данных или таблицы не существует')


    async def update_user_data(self, user_id: int, name: str = None, username: str = None) -> None:
        try:
            async with self.__async_session_factory() as session:
                user = await session.get(UsersORM, user_id)
                if name is not None:
                    user.name = name
                if username is not None:
                    user.username = username
                session.add(user)
                await session.commit()
        except sqlalchemy.exc.OperationalError:
            logging.error('Базы Данных или таблицы не существует')




    async def remove_user(self, user_id: int) -> None:
        """
        Удаляет пользователя из БД
        :param user_id: ID пользователя
        :return: None
        """
        async with self.__async_session_factory() as session:
            user = await session.get(UsersORM, user_id)
            payments = await session.execute(select(PaymentsORM).where(PaymentsORM.user_id == user_id))
            for payment in payments.scalars():
                await session.delete(payment)
            await session.delete(user)
            await session.commit()




    async def get_user_data(self, user_id: int) -> Dict:
        """
        Получает данные пользователя из Базы Данных
        :param user_id: ID пользователя
        :return: Словарь с данными пользователя по ключам согласно таблице БД.
        - id
        - name
        - username
        - subscription_end_date
        - used_generations
        - datetime_registration
        - subscription_end_date
        """
        try:
            async with self.__async_session_factory() as session:
                user_data = await session.get(UsersORM, user_id)
                return {
                    'id': user_data.id,
                    'name': user_data.name,
                    'username': user_data.username,
                    'subscription_end_date': user_data.subscription_end_date,
                    'used_generations': user_data.used_generations,
                    'datetime_registration': user_data.datetime_registration,
                    'daily_generation': user_data.daily_generation,
                }
        except AttributeError:
            logging.error("Пользователя не существует в базе данных")
            return {}

    async def subscribe_user(self, user_id: int, subscription_end_date: DateTime) -> None:
        """
        Добавляет дату окончания подписки пользователю

        :param subscription_end_date: до какого числа/времени действует подписка
        :param user_id: ID пользователя
        :return: None
        """
        try:
            async with self.__async_session_factory() as session:
                user_data = await session.get(UsersORM, user_id)
                if user_data:
                    user_data.subscription_end_date = subscription_end_date

                await session.commit()
        except AttributeError:
            logging.error("Пользователя не существует в базе данных")


    async def add_used_and_daily_generation(self, user_id: int) -> None:
        """
        Добавляет 1 генерацию в использованные (used_generations)
        :param user_id: ID пользователя
        :return: None
        """
        try:
            async with self.__async_session_factory() as session:
                user_data = await session.get(UsersORM, user_id)
                user_data.used_generations += 1
                user_data.daily_generation += 1
                await session.commit()
        except AttributeError:
            logging.error("Пользователя не существует в базе данных")

    async def add_payment(self, user_id: int, purchase_amount: int, subscription_end_date: DateTime) -> None:
        """
        Добавляет платеж в БД
        :param subscription_end_date:
        :param user_id: ID пользователя
        :param purchase_amount: Сумма платежа
        :return: None
        """
        try:
            async with self.__async_session_factory() as session:
                payment = PaymentsORM(
                    user_id=user_id,
                    purchase_amount=purchase_amount,
                    subscription_end_date=subscription_end_date,
                )
                session.add(payment)
                await session.commit()
        except sqlalchemy.exc.OperationalError:
            logging.error('Базы Данных или таблицы не существует')


    async def get_payments_of_user(self, user_id: int) -> Sequence[PaymentsORM]:
        """
        Извлекает все платежи определенного пользователя
        :param user_id: ID пользователя
        :return: None
        """

        async with self.__async_session_factory() as session:
            query = select(PaymentsORM).where(PaymentsORM.user_id == user_id)
            result = await session.execute(query)
            payments = result.scalars().all()
            return payments

    async def reset_daily_limit_for_all_users(self) -> None:
        """
        Функция для сброса лимита
        """
        try:
            async with (self.__async_session_factory() as session):
                query = select(UsersORM).order_by(UsersORM.id)
                result = await session.execute(query)
                users = result.scalars().all()
                for user in users:
                    user.daily_generation = 0
                await session.commit()
        except sqlalchemy.exc.OperationalError:
            logging.error('Базы Данных или таблицы не существует')
        return


    async def get_user_list(self) -> Sequence[UsersORM]:
        """
        Список пользователей
        """

        try:
            async with (self.__async_session_factory() as session):
                query = select(UsersORM).order_by(UsersORM.id)
                result = await session.execute(query)
                users = result.scalars().all()
                return users
        except sqlalchemy.exc.OperationalError:
            logging.error('Базы Данных или таблицы не существует')
            return []


db = Database()


async def update_user_info(message: Message) -> None:
    user_data = await db.get_user_data(user_id=message.from_user.id)
    name = message.from_user.first_name
    username = message.from_user.username

    if name != user_data.get('name') or username != user_data.get('username'):
        await db.update_user_data(message.from_user.id, message.from_user.first_name, message.from_user.username)


if __name__ == "__main__":
    print(asyncio.run(db.get_user_list()))
