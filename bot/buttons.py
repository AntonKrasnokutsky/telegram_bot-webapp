
import os

from aiogram import types
from aiogram.types.web_app_info import WebAppInfo
from dotenv import load_dotenv

load_dotenv()

URL_SERVICE = os.getenv('URL_SERVICE')
URL_REPAIR = os.getenv('URL_REPAIR')
URL_AUDIT = os.getenv('URL_AUDIT')
URL_EXTERNAL = os.getenv('URL_EXTERNAL')

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
        'Ревизия',
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
        'Ревизия',
        web_app=WebAppInfo(url=URL_AUDIT)
    ))

repairs_office_button = types.ReplyKeyboardMarkup(resize_keyboard=True)
repairs_office_button.add(
    types.KeyboardButton(
        'Ремонт',
        web_app=WebAppInfo(url=URL_EXTERNAL)
    ))
repairs_office_button.add(
    types.KeyboardButton(
        '/Зарплата',
    ))

repairs_office_button_salary = types.ReplyKeyboardMarkup(resize_keyboard=True)
repairs_office_button_salary.add(
    types.KeyboardButton(
        '/all_time',
    ))
repairs_office_button_salary.add(
    types.KeyboardButton(
        '/period',
    ))
