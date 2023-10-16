import logging
import sys
import httplib2
import json
import requests
import os
from datetime import datetime, timezone
from http import HTTPStatus
from pathlib import Path

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.web_app_info import WebAppInfo
from dotenv import load_dotenv
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
URL_SERVICE = os.getenv('URL_SERVICE')
URL_REPAIR = os.getenv('URL_REPAIR')
URL_API_POINTS = os.getenv('URL_API_POINTS')
CHAT_ID = os.getenv('CHAT_ID')
bot = Bot(TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
SHEET_SERVICE = os.getenv('SHEET_SERVICE')
SHEET_REPEAR = os.getenv('SHEET_REPEAR')
POINTS_RANGE = os.getenv('POINTS_RANGE')
SERVICEMAN_RANGE = os.getenv('SERVICEMAN_RANGE')

current_point = {}


def get_service_sacc():
    creds_json = os.path.dirname(__file__) + '/' + CREDENTIALS_FILE
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    creds_service = ServiceAccountCredentials.from_json_keyfile_name(
        creds_json,
        scopes
    ).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)


def get_list_points():
    results = get_service_sacc().spreadsheets().values().batchGet(
        spreadsheetId=SPREADSHEET_ID,
        ranges=POINTS_RANGE,
        majorDimension='COLUMNS',
        valueRenderOption='FORMATTED_VALUE',
        dateTimeRenderOption='FORMATTED_STRING'
    ).execute()
    sheet_values = results['valueRanges'][0]['values'][0]
    try:
        sheet_values.remove('')
    except ValueError:
        pass
    return sheet_values


def get_user_list():
    results = get_service_sacc().spreadsheets().values().batchGet(
        spreadsheetId=SPREADSHEET_ID,
        ranges=SERVICEMAN_RANGE,
        majorDimension='ROWS',
        valueRenderOption='FORMATTED_VALUE',
        dateTimeRenderOption='FORMATTED_STRING'
    ).execute()
    sheet_values = results['valueRanges'][0]['values']
    try:
        sheet_values.remove('')
    except ValueError:
        pass
    return sheet_values


def append_service_in_table(data: dict):
    body = {
        'values':
        [[
            data['date'],
            data['email'],
            data['fio'],
            data['point'],
            f'₽\xa0 {data["collection"]}',
            data['coffee'],
            data['cream'],
            data['chocolate'],
            data['raf'],
            data['sugar'],
            data['syrup'],
            data['glasses'],
            data['covers'],
            data['stirrer'],
            data['straws'],
        ]]}

    get_service_sacc().spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_SERVICE,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()


def append_repair_in_table(data: dict):
    body = {
        'values':
        [[
            data['date'],
            data['email'],
            data['fio'],
            data['point'],
            data['category'],
            data['repair'],
            '',
            '',
            '',
            '',
            data['description'],
        ]]}
    get_service_sacc().spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_REPEAR,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Обновление списка точек, подождите.')
    response = requests.get(URL_API_POINTS)
    if response.status_code == HTTPStatus.OK:

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            types.KeyboardButton(
                'Обслуживание',
                web_app=WebAppInfo(url=URL_SERVICE)
            ))
        markup.add(
            types.KeyboardButton(
                'Ремонт',
                web_app=WebAppInfo(url=URL_REPAIR)
            ))
        await message.answer('Бот готов к работе.', reply_markup=markup)
    else:
        await message.answer(
            'Список точек не обновлен, нажмите "/update_points" ещё раз'
        )


@dp.message_handler(commands=['update_points'])
async def update_points(message: types.Message):
    await message.answer('Обновление списка точек, подождите.')
    response = requests.get(URL_API_POINTS)
    if response.status_code == HTTPStatus.OK:
        await message.answer('Список точек обновлён')
    else:
        await message.answer(
            'Список точек не обновлён, нажмите "/update_points" ещё раз'
        )


@dp.message_handler(commands=['service'])
async def service(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton(
            'Обслуживание',
            web_app=WebAppInfo(url=URL_SERVICE)
        ))
    await message.answer('Обслуживание', reply_markup=markup)


@dp.message_handler(commands=['repair'])
async def repair(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton(
            'Ремонт',
            web_app=WebAppInfo(url=URL_REPAIR)
        ))
    await message.answer('Ремонт', reply_markup=markup)


@dp.message_handler(content_types=['web_app_data'])
async def web_app(message: types.Message):
    data = json.loads(message.web_app_data.data)
    users = get_user_list()
    data['email'] = 'Нет данных'
    data['fio'] = 'Нет данных'

    for user in users:
        if int(message.from_user.id) == int(user[2]):
            data['email'] = user[0]
            data['fio'] = user[1]
            break
    date_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
    tz = datetime.strptime('+0300', '%z').tzinfo
    date_msk = date_utc.astimezone(tz)
    data['date'] = date_msk.strftime("%d.%m.%Y %H:%M:%S")
    if data['type'] == 'service':
        data['type'] = 'Обслуживание'
        append_service_in_table(data)
    elif data['type'] == 'repair':
        data['type'] = 'Ремонт'
        append_repair_in_table(data)
    current_point[message.from_user.id] = (
        f'Вид работ: {data["type"]}\n'
        f'Точка: {data["point"]}\n'
        f'Инженер: {data["fio"]}'
    )
    message_data = ''
    message_data += f'Вид работ: {data["type"]}\n'
    message_data += f'Инженер: {data["fio"]}\n'
    message_data += f'Точка обслуживания: {data["point"]}\n'
    if data['type'] == 'Обслуживание':
        message_data += f'Инкачация: ₽\xa0 {data["collection"]}\n'
        message_data += f'Кофе: {data["coffee"]}\n'
        message_data += f'Сливки: {data["cream"]}\n'
        message_data += f'Шоколад: {data["chocolate"]}\n'
        message_data += f'Раф: {data["raf"]}\n'
        message_data += f'Сахар: {data["sugar"]}\n'
        message_data += f'Сироп: {data["syrup"]}\n'
        message_data += f'Стаканы: {data["glasses"]}\n'
        message_data += f'Крышки: {data["covers"]}\n'
        message_data += f'Размешиватели: {data["stirrer"]}\n'
        message_data += f'Трубочки: {data["straws"]}'
    elif data['type'] == 'Ремонт':
        message_data += f'Категория: {data["category"]}\n'
        message_data += f'Замена: {data["repair"]}\n'
        message_data += f'Комментарий: {data["description"]}'
    await message.answer(message_data)


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def forward_photo(message: types.Message):
    await bot.send_message(
        chat_id=CHAT_ID,
        text=current_point[message.from_user.id]
    )
    await bot.forward_message(
        chat_id=CHAT_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    executor.start_polling(dp)
