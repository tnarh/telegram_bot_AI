import logging

from googletrans import Translator

logger = logging.getLogger(__name__)


async def text_translator(text: str, src='ru', dest='en') -> str | None:
    """
    Google-переводчик текста
    :param text: Текст
    :param src: Язык текста (По-умолчанию русский)
    :param dest: Язык на который нужно перевести (По-умолчанию английский)
    :return: Переведенный текст (По-умолчанию английский), либо None, в случае неуспеха.
    """
    try:
        translator = Translator()
        translation = translator.translate(text=text, src=src, dest=dest)
        return translation.text
    except Exception as e:
        logger.error(f'Ошибка перевода текста: {e}')
        return None
