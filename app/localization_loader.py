import json
import logging
from typing import Dict

from config import LOCALES_DIR


class LocalizationLoader:
    __instance = None
    __all_messages = {}

    _PATH_TO_LANGUAGE_FILE = LOCALES_DIR + "/" + "{language}.json"
    _LANGUAGES = ['en', 'ru']
    _STANDARD_LANGUAGE = 'en'

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if not self.__all_messages:
            self.__all_messages = {lang : self.__get_messages_from_file(lang) for lang in self._LANGUAGES}


    def get_message(self, language: str, message_key: str) -> str:
        """
        Получить сообщение по языку и ключу
        :param language: язык локализации
        :param message_key: ключ сообщения
        :return: текст сообщения
        """
        if self.check_language(language):
            messages = self._load_messages(language)
        else:
            messages = self._load_messages(self._STANDARD_LANGUAGE)
        return messages.get(message_key)

    def _load_messages(self, language: str) -> Dict:
        return self.__all_messages.get(language)


    @property
    def all_messages(self) -> Dict:
        return self.__all_messages

    @classmethod
    def __get_messages_from_file(cls, language: str) -> Dict:
        path_to_file = cls._PATH_TO_LANGUAGE_FILE.format(language=language)
        try:
            logging.info(f'Запрос файла локализации: {language}')
            with open(path_to_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f'Нет файла локализации: {path_to_file}')

    @classmethod
    def check_language(cls, language):
        return language in cls._LANGUAGES

