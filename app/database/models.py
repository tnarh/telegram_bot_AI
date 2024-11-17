import datetime
from typing import Annotated

from sqlalchemy import ForeignKey, Column, DateTime
from sqlalchemy.orm import as_declarative, Mapped, mapped_column, relationship


datetime = Annotated[datetime.datetime, mapped_column(default=datetime.datetime.now())]


@as_declarative()
class Base:
    pass


class UsersORM(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column(nullable=True)
    used_generations: Mapped[int] = mapped_column(default=0)
    subscription_end_date = Column(DateTime, nullable=True)
    datetime_registration: Mapped[datetime]
    daily_generation: Mapped[int] = mapped_column(default=0)

    payments: Mapped[list["PaymentsORM"]] = relationship()


class PaymentsORM(Base):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"))
    purchase_amount: Mapped[float]
    subscription_end_date = Column(DateTime, nullable=True)
    datetime: Mapped[datetime]

    users: Mapped[list["UsersORM"]] = relationship(overlaps="payments")

