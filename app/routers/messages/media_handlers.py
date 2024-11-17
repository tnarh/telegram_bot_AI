import io
import logging

import aiohttp
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from app.database.requests import db
from app.generations import image_generate
from app import keyboards as kb
from app.states import Generation
from app.localization_loader import LocalizationLoader

locales = LocalizationLoader()
logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.message(Generation.image, F.photo)
async def get_image(message: Message, state: FSMContext) -> None:
    image = io.BytesIO()
    await message.bot.download(file=message.photo[-1].file_id, destination=image)
    await state.update_data(image=image)
    user_data = await state.get_data()
    if user_data.get('type_gen') == 'animation' or user_data.get('type_gen') == 'improve':
        await _generate_image(message, state)
        return
    else:
        await message.answer(locales.get_message(language=message.from_user.language_code,
                                                  message_key='generation_image_get_image_message'),
                             reply_markup=await kb.cancel(message.from_user.language_code))
        await state.set_state(Generation.prompt)


@router.message(Generation.prompt, F.text)
async def get_prompt(message: Message, state: FSMContext) -> None:
    await state.update_data(prompt=message.text)
    await _generate_image(message, state)


@router.message(Generation.image, ~F.image)
async def incorrect_photo(message: Message) -> None:
    await message.answer(text=locales.get_message(language=message.from_user.language_code,
                                                  message_key='download_image'),
                         reply_markup=await kb.cancel(message.from_user.language_code))


@router.message(Generation.prompt, ~F.text)
async def incorrect_prompt(message: Message) -> None:
    await message.answer(text=locales.get_message(language=message.from_user.language_code,
                                                  message_key='prompt_error'),
                         reply_markup=await kb.cancel(message.from_user.language_code))


async def _generate_image(message: Message, state: FSMContext):
    await message.answer_dice(emoji='🎲')
    await message.answer(locales.get_message(language=message.from_user.language_code,
                                             message_key='start_of_creation'))

    user_data = await state.get_data()
    image_file = user_data.get('image')
    prompt = user_data.get('prompt')
    type_gen = user_data.get('type_gen')
    logger.info(f"Пользователь: {message.from_user.id} создал запрос на генерацию: {type_gen}")

    await state.clear()
    try:
        async with ChatActionSender.upload_photo(bot=message.bot,
                                                 chat_id=message.chat.id):
            extension = 'jpg'
            match type_gen:
                case 'request':
                    url = await image_generate.generate_image_by_text_prompt(prompt=prompt)
                case 'image_and_request':
                    url = await image_generate.generate_image_by_image(image_file, extension='jpg', prompt=prompt)
                case 'improve':
                    url = await image_generate.universal_upscaler_image(image_file, extension='jpg')
                case 'animation':
                    url = await image_generate.generate_animation_by_image(image_file=image_file, extension='jpg')
                    extension = 'mp4'
            if url:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        result_bytes = await response.read()
                await message.reply_document(
                    document=types.BufferedInputFile(
                        file=result_bytes,
                        filename=locales.get_message(language=message.from_user.language_code,
                                                     message_key='result').format(extension=extension)
                    )
                )
                logger.info("Удачная отправка файла пользователю")
                await db.add_used_and_daily_generation(message.from_user.id)
    except Exception as e:
        logger.error(f"Ошибка при отправке генерации: {e}")
        await message.answer(locales.get_message(language=message.from_user.language_code,
                                                 message_key='failed_to_generate_request'),
                             reply_markup=await kb.cancel(message.from_user.language_code))
