import asyncio
from suno import Suno

from app.translator import text_translator
from config import SUNO_COOKIE




async def generate(prompt, tags):
    client = Suno(cookie=SUNO_COOKIE)
    songs = await asyncio.to_thread(client.generate,
                                    prompt=prompt,
                                    is_custom=True,
                                    tags=await text_translator(text=tags),
                                    wait_audio=True)
    return [songs[0].audio_url, songs[1].audio_url]
