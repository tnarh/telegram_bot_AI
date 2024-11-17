"""
URL: https://docs.leonardo.ai/recipes
"""

import io
import asyncio
import logging
import sys
from typing import Dict, Tuple

import leonardoaisdk
import requests
import json

from app.translator import text_translator
from config import LEONARDO_AI_TOKEN

logger = logging.getLogger(__name__)

api_key = LEONARDO_AI_TOKEN
authorization = "Bearer %s" % api_key
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": authorization
}

s = leonardoaisdk.LeonardoAiSDK(
    bearer_auth=LEONARDO_AI_TOKEN,
)


async def _upload_image(image_file: io.BytesIO, extension):
    """
    Загрузка изображения в LeonardoAI
    :param image_file:
    :param extension: png | jpg | jpeg | webp
    :return: id изображения на серверах LeonardoAI
    """

    url = "https://cloud.leonardo.ai/api/rest/v1/init-image"
    payload = {"extension": extension}
    response = requests.post(url, json=payload,
                             headers=headers)  # Получить заранее заданный URL-адрес для загрузки изображения

    # Загрузить изображение по заданному URL-адресу
    fields = json.loads(response.json()['uploadInitImage']['fields'])
    url = response.json()['uploadInitImage']['url']

    # Чтобы получить изображение позже
    image_id = response.json()['uploadInitImage']['id']
    logger.info(f"image_id: {image_id}")
    files = {'file': image_file}
    response = requests.post(url, data=fields, files=files)  # Header is not needed
    logger.info("Статус загрузки изображения по заранее указанному URL-адресу: %s" % response.status_code)
    return image_id


async def _generate_motion(payload: Dict) -> str:
    """
    Генерация видео
    :param payload:
    :return: Ссылка на видео
    """
    url = "https://cloud.leonardo.ai/api/rest/v1/generations-motion-svd"
    response = requests.post(url, json=payload, headers=headers)
    logger.info(f"Отправка запроса на анимацию: {response.json()}")
    generation_id = response.json()['motionSvdGenerationJob']['generationId']
    url = "https://cloud.leonardo.ai/api/rest/v1/generations/%s" % generation_id

    image_url = None
    result = 0
    while result != 3:
        await asyncio.sleep(60)
        try:
            response = requests.get(url, headers=headers)
            image_url = response.json()['generations_by_pk']['generated_images'][0]['motionMP4URL']
            logger.info(f"Данные анимации: {response.json()}")
            result = 3
        except Exception as e:
            logger.error(f"Ошибка при получении файла анимации: {e}")
            result += 1
    return image_url


async def _generate_image(payload: Dict) -> Tuple:
    """
    :param payload: словарь с полезной нагрузкой
    :return: URL изображения
    """
    url = "https://cloud.leonardo.ai/api/rest/v1/generations"

    response = requests.post(url, json=payload, headers=headers)
    logger.info("Статус генерации изображения: %s" % response.status_code)
    generation_id = response.json()['sdGenerationJob']['generationId']
    url = "https://cloud.leonardo.ai/api/rest/v1/generations/%s" % generation_id
    await asyncio.sleep(40)
    logger.info('Получение генерации изображения')
    response = requests.get(url, headers=headers)
    logger.info(f"Данные изображения: {response.json()}")
    try:
        image_url = response.json()['generations_by_pk']['generated_images'][0]['url']
        image_id = response.json()['generations_by_pk']['generated_images'][0]['id']
        return image_url, image_id
    except Exception as e:
        logger.error(f"Ошибка при получении сгенерированного изображения: {e}")
        await asyncio.sleep(20)
        logger.info(f"Вторая попытка получения изображения")
        try:
            response = requests.get(url, headers=headers)
            image_url = response.json()['generations_by_pk']['generated_images'][0]['url']
            image_id = response.json()['generations_by_pk']['generated_images'][0]['id']
            logger.info(f"Данные изображения: {response.json()}")
            return image_url, image_id
        except Exception as e:
            logger.error(f"Ошибка при получении сгенерированного изображения: {e}")


async def generate_image_by_text_prompt(prompt: str):
    """
    Метод Leonardo: Generate Images Using Image Prompts
    URL: https://docs.leonardo.ai/reference/creategeneration

    # Leonardo Creative model:  b24e16ff-06e3-43eb-8d33-4416c2d75876
    """
    modelId = "aa77f04e-3eec-4034-9c07-d0f619684628"  # Leonardo Kino XL model

    text = await text_translator(prompt)  # перевод текста
    logger.info(f"Подсказка: {text}")
    if not text:
        return None

    payload = {
        "num_images": 1,
        "height": 1024,
        "width": 576,
        "modelId": modelId,
        "prompt": text,
        "alchemy": True,
        "photoReal": True,
        "presetStyle": 'CINEMATIC',
        "photoRealVersion": "v2",
    }

    image_url, image_id = await _generate_image(payload=payload)
    s.image.delete_generation_by_id(id=image_id)
    return image_url


async def generate_image_by_image(image_file: io.BytesIO, extension: str, prompt: str) -> str | None:
    """
    Метод Leonardo: Generate with Image to Image Guidance using Uploaded Images
    Url: https://docs.leonardo.ai/reference/creategeneration
    :param image_file: файл
    :param extension: расширение файла
    :param prompt: текстовая подсказка для изображения
    :return: URL изображения

    Доступные модели:

    - Standard: 1e60896f-3c26-4296-8ecc-53e2afecc132
    - Leonardo Kino XL: aa77f04e-3eec-4034-9c07-d0f619684628
    - Other: b24e16ff-06e3-43eb-8d33-4416c2d75876
    """
    modelId = "aa77f04e-3eec-4034-9c07-d0f619684628"

    text = await text_translator(prompt)  # перевод текста
    logger.info(f"Подсказка: {text}")
    if not text:
        return None

    image_id = await _upload_image(image_file, extension)

    payload = {
        "num_images": 1,
        "height": 1024,
        "width": 576,
        "modelId": modelId,
        "prompt": text,
        "alchemy": True,
        "photoReal": True,
        "presetStyle": 'CINEMATIC',
        "photoRealVersion": "v2",

        "controlnets": [
            {
                "initImageId": image_id,
                "initImageType": "UPLOADED",
                "preprocessorId": 133,
                "strengthType": "Mid",
            },
        ],

    }
    image_url, image_id = await _generate_image(payload=payload)
    s.image.delete_generation_by_id(id=image_id)
    return image_url


async def generate_animation_by_image(image_file: io.BytesIO, extension: str):
    """
    Метод Leonardo: Generate Motion Using Uploaded Images
    url: https://docs.leonardo.ai/docs/generate-motion-using-uploaded-images
    """
    image_id = await _upload_image(image_file, extension)
    logger.info(f'image_id: {image_id}')
    payload = {
        "imageId": image_id,
        "isInitImage": True,
        "motionStrength": 2,
    }
    url_motion = await _generate_motion(payload=payload)
    return url_motion


async def universal_upscaler_image(image_file: io.BytesIO, extension: str):
    """
    Метод Leonardo: Create using Universal Upscaler
    url: https://docs.leonardo.ai/docs/image-variations-with-universal-upscaler
    """
    url = "https://cloud.leonardo.ai/api/rest/v1/variations/universal-upscaler"
    image_id = await _upload_image(image_file, extension)
    logger.info(f'image_id: {image_id}')

    payload = {
        "upscalerStyle": "GENERAL",
        "creativityStrength": 3,
        "upscaleMultiplier": 1.5,
        "initImageId": image_id
    }

    response = requests.post(url, json=payload, headers=headers)
    logger.info("Статус генерации изображения: %s" % response.status_code)
    variation_id = response.json()['universalUpscaler']['id']
    url = "https://cloud.leonardo.ai/api/rest/v1/variations/%s" % variation_id
    await asyncio.sleep(70)
    response = requests.get(url, headers=headers)
    logger.info(f"Данные изображения: {response.json()}")
    try:
        image_url = response.json()['generated_image_variation_generic'][0]['url']
        image_id = response.json()['generated_image_variation_generic'][0]['id']
        return image_url
    except Exception as e:
        logger.error(f"Ошибка при получении сгенерированного изображения: {e}")
        await asyncio.sleep(20)
        logger.info(f"Вторая попытка получения изображения")
        try:
            await asyncio.sleep(20)
            logger.info(f"Вторая попытка получения изображения")
            response = requests.get(url, headers=headers)
            image_url = response.json()['generated_image_variation_generic'][0]['url']
            image_id = response.json()['generated_image_variation_generic'][0]['id']
            logger.info(f"Данные изображения: {response.json()}")
            return image_url
        except Exception as e:
            logger.error(f"Ошибка при получении сгенерированного изображения: {e}")


async def get_api_subscription_tokens() -> str | int:
    try:
        data = s.user.get_user_self()
        api_subscription_tokens = data.object.user_details[0].api_subscription_tokens
        return api_subscription_tokens
    except leonardoaisdk.models.errors.sdkerror.SDKError as e:
        error_mess = 'Ошибка при получении количества токенов LeonardoAI'
        logger.error(f"{error_mess}: {e}")
        return error_mess


if __name__ == "__main__":
    IMAGE_FILE = "../data/media/original.jpg"
    with open(IMAGE_FILE, 'rb') as file:
        image_bytes = io.BytesIO(file.read())
        # asyncio.run(generate_image_by_image(image_bytes, prompt="Супергерой из marvel который может всё, а на заднем фоне крутая машина", extension='jpg'))
        # asyncio.run(generate_motion_by_image(image_file=image_bytes, extension='jpg'))
        # asyncio.run(universal_upscaler_image(image_file=image_bytes, extension='jpg'))

        # image_bytes = io.BytesIO(file.read())
        # asyncio.run(generate_image_by_image(image_bytes, prompt="Create an image of a bear in sea.", extension='jpg'))

    # asyncio.run(generate_image_by_text_prompt(prompt="Супергерой из marvel который может всё"))
    print(asyncio.run(get_api_subscription_tokens()))
