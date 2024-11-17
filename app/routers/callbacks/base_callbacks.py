import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app import keyboards as kb
from app.database.requests import db
from app.filters.user_filters import Subscribe, Admins
from app.generations.image_generate import get_api_subscription_tokens
from app.prices import Prices
from app.routers.payment.base_payment import invoice
from app.states import Generation, GenerationMusic
from app.localization_loader import LocalizationLoader

locales = LocalizationLoader()
logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(kb.DaysPriceCallbackData.filter())
async def buy(callback: CallbackQuery,
              callback_data: kb.DaysPriceCallbackData,
              state: FSMContext) -> None:
    """
    Отрабатывает на выбор определенного кол-ва генераций при покупке, а также добавляет это количество в кэш
    :param state:
    :param callback: Callback запрос
    :param callback_data: Строка-запроса сформированная для кнопки на клавиатуре
    """
    await callback.message.delete()
    days = callback_data.days
    price = callback_data.price
    data = await state.get_data()
    await state.update_data(days=days)
    await invoice(callback, price=price, payment_type=data.get('payment_type'))


@router.callback_query(F.data == 'account', Admins())
async def handler_account(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    # await callback.message.delete()
    tokens = await get_api_subscription_tokens()
    await callback.message.edit_text(text=locales.get_message(language=callback.from_user.language_code,
                                                              message_key='text_for_admins_profile').format(
        name=callback.from_user.first_name,
        user_id=callback.from_user.id,
        tokens=tokens),
        reply_markup=await kb.personal_area(callback.from_user.language_code))


@router.callback_query(F.data == 'account')
async def handler_account(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    # await callback.message.delete()
    user_id = callback.from_user.id
    user_data = await db.get_user_data(user_id)
    if user_data:
        if user_data['subscription_end_date']:
            subscription_end_date = user_data['subscription_end_date'].strftime("%d.%m.%Y %H:%M")
        else:
            subscription_end_date = locales.get_message(language=callback.from_user.language_code,
                                                        message_key='not_subscribe')
        await callback.message.edit_text(text=locales.get_message(language=callback.from_user.language_code,
                                                                         message_key='text_for_profile').format(
                                                    name=callback.from_user.first_name,
                                                    user_id=user_id,
                                                    subscription_end_date=subscription_end_date,
                                                    used_generations=user_data['used_generations']
                                                ),
                                                reply_markup=await kb.cancel(callback.from_user.language_code))
    else:
        await callback.message.answer(locales.get_message(language=callback.from_user.language_code,
                                                          message_key='press_start'))


@router.callback_query(F.data == 'newsletter', Admins())
async def handler_newsletter(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(locales.get_message(language=callback.from_user.language_code,
                                                         message_key='write_your_message_for_mailing'),
                                     reply_markup=await kb.cancel(callback.from_user.language_code))
    await state.set_state(Generation.newsletter)


@router.callback_query(F.data == 'send_newsletter', Admins())
async def handler_send_newsletter(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.delete()
    user_data = await state.get_data()
    message_id = user_data.get('message_id')
    chat_id = callback.message.chat.id

    await state.clear()

    users = await db.get_user_list()
    count = 0
    for u in users:
        try:
            await callback.bot.copy_message(chat_id=u.id, from_chat_id=chat_id,
                                            message_id=message_id)
            count += 1
        except Exception as e:
            await db.remove_user(user_id=u.id)
            logger.error(f'Ошибка отправки сообщения пользователю:{u.id} - {e}')

    await callback.bot.delete_message(callback.message.chat.id, message_id=message_id)
    await callback.message.answer(
        locales.get_message(language=callback.from_user.language_code, message_key='count_messages_sent_from').format(
            count=count, len_users=len(users)))


@router.callback_query(F.data == 'cancel')
async def handler_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        locales.get_message(language=callback.from_user.language_code, message_key='start_message'),
        reply_markup=await kb.start_menu(callback.from_user.language_code))


@router.callback_query(F.data == 'buy')
async def handler_cancel(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        locales.get_message(language=callback.from_user.language_code, message_key='select_payment_method'),
        reply_markup=await kb.payments(callback.from_user.language_code))


@router.callback_query(F.data == 'generation', Subscribe())
async def handler_generation_types(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    # await callback.message.delete()
    await callback.message.edit_text(
                                            text=locales.get_message(language=callback.from_user.language_code,
                                                                     message_key='what_do_you_want'),
                                            reply_markup=await kb.generations_menu(callback.from_user.language_code))


@router.callback_query(F.data == 'generation', ~Subscribe())
async def handler_type_cloth_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Отрабатывает при неоформленной подписке
    :param state:
    :param callback: Callback запрос
    """
    await state.clear()
    # await callback.message.delete()
    await callback.message.edit_text(text=locales.get_message(language=callback.from_user.language_code,
                                                                     message_key='not_available_generations_message'),
                                            reply_markup=await kb.cancel(callback.from_user.language_code))


@router.callback_query(kb.TypeGenerationCallbackData.filter(), Subscribe())
async def handler_generation(callback: CallbackQuery,
                             callback_data: kb.TypeGenerationCallbackData,
                             state: FSMContext) -> None:
    """
    Отрабатывает при оформленной подписке
    :param state:
    :param callback: Callback запрос
    :param callback_data: Строка-запроса сформированная для кнопки на клавиатуре
    """
    type_gen = callback_data.type_gen
    await state.update_data(type_gen=type_gen)

    match type_gen:
        case 'request':
            await callback.message.edit_text(
                locales.get_message(language=callback.from_user.language_code, message_key='generation_prompt_message'),
                reply_markup=await kb.cancel(callback.from_user.language_code))
            await state.set_state(Generation.prompt)
        case 'image_and_request':
            await callback.message.edit_text(
                locales.get_message(language=callback.from_user.language_code, message_key='generation_image_message'),
                reply_markup=await kb.cancel(callback.from_user.language_code))
            await state.set_state(Generation.image)
        case 'animation':
            await callback.message.edit_text(
                locales.get_message(language=callback.from_user.language_code, message_key='generation_image_message'),
                reply_markup=await kb.cancel(callback.from_user.language_code))
            await state.set_state(Generation.image)
        case 'improve':
            await callback.message.edit_text(
                locales.get_message(language=callback.from_user.language_code, message_key='generation_image_message'),
                reply_markup=await kb.cancel(callback.from_user.language_code))
            await state.set_state(Generation.image)

        case 'music_create':
            await callback.message.edit_text(
                locales.get_message(language=callback.from_user.language_code, message_key='music_creation_message'),
                reply_markup=await kb.cancel(callback.from_user.language_code))
            await state.set_state(GenerationMusic.lyric)


@router.callback_query(kb.PaymentTypeCallbackData.filter())
async def handler_generation(callback: CallbackQuery,
                             callback_data: kb.PaymentTypeCallbackData,
                             state: FSMContext) -> None:
    language = callback.from_user.language_code
    payment_type = callback_data.payment_type
    await state.update_data(payment_type=payment_type)
    message_text = locales.get_message(language=language, message_key='buy_message')
    price_days = await Prices.get_prices_and_days(payment_type=payment_type)
    for price, days in price_days.items():
        message_text += locales.get_message(language=language, message_key=f'{payment_type}_prices_message').format(
            price, days)

    await callback.message.edit_text(text=message_text,
                                     reply_markup=await kb.price(language, payment_type))
