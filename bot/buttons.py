
import os

from aiogram import types
from aiogram.types.web_app_info import WebAppInfo
from dotenv import load_dotenv

load_dotenv()

URL_SERVICE = os.getenv('URL_SERVICE')
URL_REPAIR = os.getenv('URL_REPAIR')
URL_AUDIT = os.getenv('URL_AUDIT')

service_button = types.ReplyKeyboardMarkup(resize_keyboard=True).add(
    types.KeyboardButton(
        'Обслуживание',
        web_app=WebAppInfo(url=URL_SERVICE)
    ))
repair_button = types.ReplyKeyboardMarkup(resize_keyboard=True).add(
    types.KeyboardButton(
        'Ремонт',
        web_app=WebAppInfo(url=URL_REPAIR)
    ))
audit_button = types.ReplyKeyboardMarkup(resize_keyboard=True).add(
    types.KeyboardButton(
        'Инвертаризация',
        web_app=WebAppInfo(url=URL_AUDIT)
    ))

start_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
start_buttons.add(
    types.KeyboardButton(
        'Обслуживание',
        web_app=WebAppInfo(url=URL_SERVICE)
    ))
start_buttons.add(
    types.KeyboardButton(
        'Ремонт',
        web_app=WebAppInfo(url=URL_REPAIR)
    ))
start_buttons.add(
    types.KeyboardButton(
        'Инветаризация',
        web_app=WebAppInfo(url=URL_AUDIT)
    ))
