from aiogram.fsm.state import State, StatesGroup


class Generation(StatesGroup):
    prompt = State()
    image = State()
    newsletter = State()


class GenerationMusic(StatesGroup):
    lyric = State()
    tag = State()
