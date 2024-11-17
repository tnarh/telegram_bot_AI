import logging

from aiogram import Router, F
from aiogram.client.session import aiohttp
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from aiogram.utils.chat_action import ChatActionSender

from app import keyboards as kb
from app.database.requests import db
from app.generations.music_generate import generate
from app.states import Generation, GenerationMusic
from app.localization_loader import LocalizationLoader

logger = logging.getLogger(__name__)
locales = LocalizationLoader()
router = Router(name=__name__)



@router.message(Generation.newsletter)
async def get_prompt(message: Message, state: FSMContext) -> None:
    await state.update_data(message_id=message.message_id)
    await message.answer(text=locales.get_message(language=message.from_user.language_code,
                                                  message_key='are_you_sure'),
                         reply_markup=await kb.send_newsletter(message.from_user.language_code))


@router.message(F.text, GenerationMusic.lyric)
async def get_lyric(message: Message, state: FSMContext):
    """ Получает текст для музыкального произведения """
    await state.set_data({'lyric': message.text})
    await state.set_state(GenerationMusic.tag)
    await message.reply(
        text=locales.get_message(language=message.from_user.language_code,
                                 message_key='generation_music_lyric'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text=locales.get_message(language=message.from_user.language_code,
                                 message_key='cancel'), callback_data='cancel')
        ]]))


@router.message(F.text, GenerationMusic.tag)
async def get_tag_n_generate(message: Message, state: FSMContext):
    """ Получает стиль для музыкального произведения """

    await message.answer_dice('🎲')
    data = await state.get_data()
    logger.info(f"Пользователь: {message.from_user.id} создал запрос на генерацию музыки")

    await state.clear()
    try:
        await message.answer(
            text=locales.get_message(language=message.from_user.language_code, message_key='generate_music_message')

        )

        async with ChatActionSender.record_voice(bot=message.bot,
                                                 chat_id=message.chat.id):
            link = await generate(data['lyric'], message.text)
            async with aiohttp.ClientSession() as session:
                async with session.get(link[0]) as response:
                    result_bytes = await response.read()
                    await message.reply_document(document=BufferedInputFile(
                        file=result_bytes, filename='music.mp3'))
                await message.answer(
                    text=locales.get_message(language=message.from_user.language_code, message_key='generate_music_second_message')

                )
                async with session.get(link[1]) as response:
                    result_bytes = await response.read()
                    await message.reply_document(document=BufferedInputFile(
                        file=result_bytes, filename='music.mp3'))
                await db.add_used_and_daily_generation(message.from_user.id)
    except Exception as e:
        logger.error(f"Ошибка при отправке генерации: {e}")
        await message.answer(
            text=locales.get_message(language=message.from_user.language_code, message_key='generate_music_error_message'),
            reply_markup=await kb.cancel(message.from_user.language_code))
