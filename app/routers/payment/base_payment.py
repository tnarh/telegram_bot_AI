import datetime
import json
import logging
from datetime import timedelta

import aiogram
from aiogram.fsm.context import FSMContext
from aiogram.types import LabeledPrice
from aiogram import types, Router, F, html

from app.database.requests import db
from config import YKASSA_PAYMENT_TOKEN, STRIPE_PAYMENT_TOKEN
from app.localization_loader import LocalizationLoader

logger = logging.getLogger(__name__)
locales = LocalizationLoader()
router = Router()


async def invoice(callback, price: float, payment_type: str) -> None:
    """
    :param payment_type:
    :param callback:
    :param price: num
    :return:
    """
    if payment_type == 'stripe':
        TOKEN = STRIPE_PAYMENT_TOKEN
        currency = 'usd'
    else:
        TOKEN = YKASSA_PAYMENT_TOKEN
        currency = 'rub'

    generation_text = locales.get_message(language=callback.from_user.language_code,
                                          message_key='generations')
    activate_generation_text = locales.get_message(language=callback.from_user.language_code,
                                                   message_key='activate_generations')
    try:
        await callback.bot.send_invoice(
            chat_id=callback.message.chat.id,
            title=generation_text,
            description=activate_generation_text,
            provider_token=TOKEN,
            currency=currency,
            # is_flexible=False,
            prices=[
                LabeledPrice(label=generation_text, amount=100 * int(price)),
            ],
            payload='invoice-payload',
            provider_data=json.dumps(
                {'receipt':
                    {'items': [
                        {'description': activate_generation_text,
                         'quantity': '1',
                         'amount': {
                             'value': str(price),
                             'currency': currency.upper(),
                         },
                         'vat_code': 1,
                         }
                    ], 'email': 'mail@mail.ru',
                    },

                }),
            need_email=False,
            send_email_to_provider=False,
        )
    except aiogram.exceptions.TelegramBadRequest as e:
        logger.error(f'Ошибка при оплате подписки: {e} | TOKEN = {TOKEN} | PAYMENT TYPE = {payment_type}')
        await callback.bot.send_message(chat_id=callback.message.chat.id,
                                        text=locales.get_message(language=callback.from_user.language_code,
                                                                 message_key='error_invoice'))


@router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery) -> None:
    """
    Как только пользователь подтвердит свои данные об оплате и доставке,
     Bot API отправляет окончательное подтверждение в форме обновления с полем pre_checkout_query
    :param pre_checkout_query: Уникальный идентификатор запроса, на который необходимо ответить.
    """
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id,
                                                           ok=True)  # Укажите True, если все в порядке (товар есть в наличии и т.п.)
    # и бот готов приступить к оформлению заказа.
    # Используйте False, если есть какие-либо проблемы.


@router.message(F.successful_payment)
async def successful_payment(message: types.Message,
                             state: FSMContext) -> None:
    """
    Метод при успешном платеже.
    Получает основную информацию об успешном платеже и сохраняет запись в базе данных
    """
    user_id = message.from_user.id
    purchase_amount = message.successful_payment.total_amount // 100
    user_data_cache = await state.get_data()
    user_data = await db.get_user_data(message.from_user.id)

    subscription_end_date_actual = user_data['subscription_end_date']
    if subscription_end_date_actual:
        subscription_end_date = subscription_end_date_actual + timedelta(days=user_data_cache['days'])
    else:
        subscription_end_date = datetime.datetime.now() + timedelta(days=user_data_cache['days'])

    await db.subscribe_user(user_id, subscription_end_date)
    await db.add_payment(user_id, purchase_amount, subscription_end_date)
    await message.bot.send_message(message.chat.id, text=locales.get_message(language=message.from_user.language_code,
                                                                             message_key='successful_payment').format(
        date=subscription_end_date.strftime('%d.%m.%Y %H:%M')))
