import logging

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, FSInputFile

from app import keyboards as kb
from app.database.requests import db, update_user_info
from app.filters.user_filters import Admins, UserInDatabase
from app.generations.image_generate import get_api_subscription_tokens
from app.localization_loader import LocalizationLoader
from config import MEDIA_DIR

logger = logging.getLogger(__name__)
router = Router(name=__name__)

VIDEO = FSInputFile(f'{MEDIA_DIR}/promo.mp4')
locales = LocalizationLoader()


@router.message(CommandStart(),
                UserInDatabase(),
                default_state)
async def command_start_handler(message: Message) -> None:
    await update_user_info(message)
    await message.answer(text=locales.get_message(language=message.from_user.language_code,
                                                         message_key='start_message'),
                         reply_markup=await kb.start_menu(message.from_user.language_code))


@router.message(CommandStart(),
                UserInDatabase()
                )
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await update_user_info(message)
    await message.answer(text=locales.get_message(language=message.from_user.language_code,
                                                         message_key='start_message'),
                         reply_markup=await kb.start_menu(message.from_user.language_code))
    await state.clear()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await db.add_user(user_id=message.from_user.id, name=message.from_user.first_name, username=message.from_user.username)
    await message.bot.send_video(chat_id=message.chat.id,
                                 caption=locales.get_message(language=message.from_user.language_code,
                                                             message_key='start_message_for_new_users').format(
                                     name=message.from_user.first_name),
                                 allow_sending_without_reply=True,
                                 video=VIDEO,
                                 # reply_markup=await kb.start_menu(message.from_user.language_code),
                                 )


@router.message(Command('help'))
async def command_help_handler(message: Message, state: FSMContext) -> None:
    """
    Метод для обработки команды '/help', для отправки инструктирующего сообщения.
    :param message: Сообщение-entity
    :param state: Состояние
    """
    await state.clear()
    await message.answer(text=locales.get_message(language=message.from_user.language_code, message_key='help_message'),
                         reply_markup=await kb.start_menu(message.from_user.language_code))


@router.message(Command('buy'))
async def command_buy_handler(message: Message, state: FSMContext) -> None:
    """
    Метод для обработки команды '/buy', для покупки генераций.
    :param message: Сообщение-entity
    :param state: Состояние
    """
    await state.clear()
    language = message.from_user.language_code
    message_text = locales.get_message(language=language, message_key='select_payment_method')
    await message.answer(text=message_text, reply_markup=await kb.payments(language))


@router.message(Command('get_user_list'), Admins())
async def command_get_user_list_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    users_sequence = await db.get_user_list()
    users_list = []
    count = 0
    for i, user in enumerate(users_sequence, start=1):
        users_list.append(
            f'{i}. {user.name} - {f"@{user.username}" if user.username else locales.get_message(language=message.from_user.language_code, message_key="not_login")}')
        count += 1
        if count == 70:
            await message.answer(
                locales.get_message(language=message.from_user.language_code, message_key='get_user_list')
                + '\n'.join(users_list),
                reply_markup=await kb.cancel(message.from_user.language_code))
            count = 0
            users_list = []
    if users_list:
        await message.answer(
            locales.get_message(language=message.from_user.language_code, message_key='get_user_list') + '\n'.join(
                users_list), reply_markup=await kb.cancel(message.from_user.language_code))


@router.message(Command('account'), Admins())
async def command_account_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    tokens = await get_api_subscription_tokens()
    await message.answer(
        locales.get_message(language=message.from_user.language_code, message_key='text_for_admins_profile').format(
            name=message.from_user.first_name,
            user_id=message.from_user.id,
            tokens=tokens), reply_markup=await kb.personal_area(message.from_user.language_code))


@router.message(Command('account'), UserInDatabase())
async def command_account_handler(message: Message, state: FSMContext) -> None:
    await state.clear()

    user_id = message.from_user.id
    user_data = await db.get_user_data(user_id)
    if user_data.get('subscription_end_date'):
        subscription_end_date = user_data.get('subscription_end_date').strftime("%d.%m.%Y %H:%M")
    else:
        subscription_end_date = locales.get_message(language=message.from_user.language_code,
                                                    message_key='not_subscribe')
    await message.answer(locales.get_message(language=message.from_user.language_code,
                                             message_key='text_for_profile').format(
        name=message.from_user.first_name,
        user_id=user_id,
        subscription_end_date=subscription_end_date, used_generations=user_data.get('used_generations')))


@router.message(Command('account'))
async def command_account_handler(message: Message) -> None:
    await message.answer(locales.get_message(language=message.from_user.language_code,
                                             message_key='press_start'))



# async def get_subscription_end_date