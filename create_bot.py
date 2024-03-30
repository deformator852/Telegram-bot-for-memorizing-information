from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
import os

TOKEN = "6261314397:AAFRs5_y2yl5J542IjzqYUc_9Vgb7xZksK8"
ADMINS_ID = [
    466296371,
]
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
