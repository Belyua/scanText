import os
import requests
import sqlite3
import aiogram.utils.markdown as md
from typing import List
from aiogram.types import Message
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram import Bot, Dispatcher, executor, types

from main import warped

API_TOKEN = '6030401447:AAGULaoiwtU9QL4k9juwd0o1u-kLjv7t3oY'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot,
                storage=storage)
files = {'photo': open('images/img.png', 'rb')}

# For example use simple SQLite storage for Dispatcher.


@dp.message_handler(commands=['start', 'help'])
async def cmd_start(message):
    await message.answer(
        "Hi there! I am a scanner bot.\n"
        "Use the /send_photo command to scan your document.")


@dp.message_handler(commands=['send_photo'])
async def on_photos(message: List[Message]) -> None:

    await message.answer(
        warped
    )


def save_to_db(image_id, image):
    conn = sqlite3.connect("images.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS images (id TEXT, photo BLOB NOT NULL)")
    cursor.execute("INSERT INTO images VALUES (?, ?)", (image_id, image))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
#
# if __name__ == '__main__':
#     bot = Bot(API_TOKEN)
#
#     # For example use Long Polling.
#     dp = Dispatcher(bot)
#
#     from aiogram.contrib.middlewares.logging import LoggingMiddleware
#     dp.middleware.setup(LoggingMiddleware())
#
#     # Setup photo handler
#     dp.message_handler(content_types=['photo'], photos_allowed=True, callback=on_photos)
#
#     executor.start_polling(dp, on_startup=on_pre_startup, on_shutdown=on_pre_shutdown)
