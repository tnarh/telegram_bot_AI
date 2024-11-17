"""
URL: https://lumalabs.ai/dashboard/api
"""
import io
import asyncio
import logging
from typing import Dict

import requests

from app.translator import text_translator
from config import LUMA_API_TOKEN

logger = logging.getLogger(__name__)


api_key = LUMA_API_TOKEN
url = "https://webapp.engineeringlumalabs.com/api/v2/capture/credits"

headers = {
  'Authorization': 'luma-api-key={}'.format(api_key)
}


async def get_video_by_text_prompt(prompt: str):

    video_title = await text_translator(prompt)

    response = requests.post("https://webapp.engineeringlumalabs.com/api/v2/capture",
                             headers=headers,
                             data={'title': video_title})
    capture_data = response.json()
    upload_url = capture_data['signedUrls']['source']
    slug = capture_data['capture']['slug']

    logger.info(f'Create: upload_url: {upload_url} slug: {slug}')

    with open("../data/media/promo.mp4", "rb") as f:
        payload = f.read()

    # upload_url from step (1)
    response = requests.put(upload_url, headers={'Content-Type': 'text/plain'}, data=payload)
    logger.info(f'Upload: {response}')

    # Note: the payload should be bytes containing the file contents (as shown above)!
    # A common pitfall is uploading the file name as the file contents
    # slug from Capture step

    response = requests.post(f"https://webapp.engineeringlumalabs.com/api/v2/capture/{slug}",
                             headers=headers)
    logger.info(f'Trigger: {response}')
    # slug from Capture step

    auth_headers = {
        'Authorization': 'luma-api-key=276a3f73-6b08-4ac6-b88d-32f900a3431d-341c61b-7931-473e-ad26-14daae60981d'}
    response = requests.get(f"https://webapp.engineeringlumalabs.com/api/v2/capture/{slug}",
                            headers=auth_headers)

    logger.info(f'Check and Download response: {response}')
    logger.info(f'Check and Download text: {response.text}')
    logger.info(f'Check and Download json: {response.json()}')





async def get_api_subscription_tokens() -> Dict:
    """
    Получает информацию о токенах

    :returns: Словарь с данными о токенах
    - *remaining*: Остаток доступных токенов.
    - *used*: Количество использованных токенов.
    - *total*: Общее количество токенов.
    :rtype: Dict
    """
    api_subscription_tokens = requests.request("GET", url, headers=headers, data={})
    return api_subscription_tokens.json()

