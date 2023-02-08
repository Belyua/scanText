import os
import io
from io import BytesIO
from eyes import four_point_transform
from skimage.filters import threshold_local
import numpy as np
from PIL import Image
import cv2
import aiogram.utils
import imutils
import telegram
import requests
import sqlite3
import aiogram.utils.markdown as md
from typing import List
from aiogram.types import Message, ContentType, InputFile
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram import Bot, Dispatcher, executor, types
from main import main
from matplotlib import pyplot as plt

bot = Bot(token=os.environ.get('TOKEN'), parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot,
                storage=storage)


# For example use simple SQLite storage for Dispatcher.
@dp.message_handler(commands=['start', 'help'])
async def cmd_start(message):
    await message.answer(
        "Hi there! I am a scanner bot.\n"
        "Use the /send_photo command to scan your document.")


@dp.message_handler(content_types=[ContentType.PHOTO])
async def on_photos(message: InputFile) -> None:

    photo = message.photo[-1]
    image_binary = BytesIO()
    #await bot.download_file(photo.file_id, image_binary)
    pil_image = np.array(Image.open(image_binary))
    image = cv2.imread(pil_image)
    ratio = image.shape[0] / 500.0
    orig = image.copy()
    image = imutils.resize(image, height=500)

    # convert the image to grayscale, blur it, and find edges in the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)

    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]
    # loop over the contours
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # if our approximated contour has four points, then we
        # can assume that we have found our screen
        if len(approx) == 4:
            screenCnt = approx
            break
    # show the contour (outline) of the piece of paper
    print("STEP 2: Find contours of paper")
    # apply the four point transform to obtain a top-down
    # view of the original image
    warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
    # convert the warped image to grayscale, then threshold it
    # to give it that 'black and white' paper effect
    warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    T = threshold_local(warped, 11, offset=10, method="gaussian")
    warped = (warped > T).astype("uint8") * 255
    # show the original and scanned images
    print("STEP 3: Apply perspective transform")

    img = Image.fromarray(warped)

    img.save(binary_stream, format='jpeg')
    binary_stream.seek(0)
    await bot.send_photo(chat_id=368692515, photo=InputFile(binary_stream))
    #await bot.send_photo(chat_id=, photo=img)
    #await message.answer(InputFile(bio))


# def save_to_db(image_id, image):
#     conn = sqlite3.connect("images.db")
#     cursor = conn.cursor()
#     cursor.execute("CREATE TABLE IF NOT EXISTS images (id TEXT, photo BLOB NOT NULL)")
#     cursor.execute("INSERT INTO images VALUES (?, ?)", (image_id, image))
#     conn.commit()
#     conn.close()

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
