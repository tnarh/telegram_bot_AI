from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.localization_loader import LocalizationLoader
from app.prices import Prices
from config import TELEGRAM_CHANEL_URL


locales = LocalizationLoader()


class DaysPriceCallbackData(CallbackData, prefix="days"):
    days: int
    price: float


class TypeGenerationCallbackData(CallbackData, prefix="type_gen"):
    type_gen: str


class PaymentTypeCallbackData(CallbackData, prefix="payment"):
    payment_type: str


async def start_menu(language):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='start_button'), callback_data='generation'))
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='personal_account_button'), callback_data='account'))
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='buy_button'), callback_data='buy'))
    keyboard.adjust(1)
    return keyboard.as_markup()


async def personal_area(language):
    keyboard = InlineKeyboardBuilder()
    # keyboard.add(InlineKeyboardButton(text='Начать', callback_data='generation'))
    # keyboard.add(InlineKeyboardButton(text='Оставшиеся токены', callback_data='tokens'))
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='sending_a_message_button'), callback_data='newsletter'))
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='back_button'), callback_data='cancel'))
    keyboard.adjust(1)
    return keyboard.as_markup()


async def generations_menu(language):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='create_an_image_upon_request_button'),
                                      callback_data=TypeGenerationCallbackData(type_gen='request').pack()))
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='create_a_piece_of_music_button'),
                                      callback_data=TypeGenerationCallbackData(type_gen='music_create').pack()))
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='change_your_photo_button'),
                                      callback_data=TypeGenerationCallbackData(type_gen='image_and_request').pack()))
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='animate_a_picture_button'),
                                      callback_data=TypeGenerationCallbackData(type_gen='animation').pack()))
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='improve_photo_quality_button'),
                                      callback_data=TypeGenerationCallbackData(type_gen='improve').pack()))
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='video_translator_button'),
                                      url='https://t.me/Video_translator_Aurora_bot'
                 ))
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='back_button'), callback_data='cancel'))
    keyboard.adjust(1)
    return keyboard.as_markup()


async def cancel(language):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='menu_button'), callback_data='cancel'))
    return keyboard.as_markup()


async def send_newsletter(language):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='send_button'), callback_data='send_newsletter'))
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='cancel_button'), callback_data='cancel'))
    return keyboard.as_markup()


async def subscribe(language):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='subscribe_button'), url=TELEGRAM_CHANEL_URL))
    return keyboard.as_markup()



async def price(language, payment_type):
    keyboard = InlineKeyboardBuilder()
    price_days = await Prices.get_prices_and_days(payment_type=payment_type)
    currency = ' $ ' if payment_type == 'stripe' else ' ₽ '
    for days, price in price_days.items():

        keyboard.button(text=str(price) + currency, callback_data=DaysPriceCallbackData(days=days, price=price).pack())
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='cancel_button'), callback_data='cancel'))
    keyboard.adjust(1)
    return keyboard.as_markup()


async def payments(language):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='ykassa'), callback_data=PaymentTypeCallbackData(payment_type='ykassa').pack()))
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='stripe'), callback_data=PaymentTypeCallbackData(payment_type='stripe').pack()))
    keyboard.add(InlineKeyboardButton(text=locales.get_message(language=language,
                                                               message_key='cancel_button'), callback_data='cancel'))
    keyboard.adjust(2)
    return keyboard.as_markup()

