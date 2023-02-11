import os

from main import main
from aiogram.types import Message, ContentType, InputFile
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor, types


bot = Bot(token=os.environ.get('TOKEN'), parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot,
                storage=storage)


@dp.message_handler(commands=['start', 'help'])
async def cmd_start(message):
    await message.answer(
        "Hi there! I am a scanner bot.\n"
        "Use the /send_photo command to scan your document.")


@dp.message_handler(content_types=[ContentType.PHOTO])
async def on_photos(message: InputFile) -> None:
    await message.photo[-1].download('test.jpg')
    await bot.send_photo(chat_id=message.chat.id, photo=InputFile(main('test.jpg')))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
