import json
import os
from datetime import datetime

from http import HTTPStatus
import httplib2
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.web_app_info import WebAppInfo
from dotenv import load_dotenv
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
URL = os.getenv('URL')
URL_API = os.getenv('URL_API')
bot = Bot(TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
SHEET_ID = os.getenv('SHEET_ID')


def get_service_sacc():
    creds_json = os.path.dirname(__file__) + '/' + CREDENTIALS_FILE
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    creds_service = ServiceAccountCredentials.from_json_keyfile_name(
        creds_json,
        scopes
    ).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)


def append_in_table(data: dict):
    body = {
        'values':
        [[
            str(datetime.now())[:19],
            data['user'],
            'ФИО',
            data['point'],
            f'₽1\xa0{data["collection"]}',
            data['coffee'],
            data['cream'],
            data['chocolate'],
            data['raf'],
            data['sugar'],
            data['syrup'],
            data['glasses'],
            data['covers'],
            data['stirrer'],
            data['collection'],
            '',
            '',
            '',
            '',
            '',
            'photo'
        ]]}
    get_service_sacc().spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='Лист1',
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    points = {
        'names': [
            'Имя 1',
            'Имя 2'
        ]
    }
    response = requests.post(URL_API, json=json.dumps(points))
    if response.status_code == HTTPStatus.CREATED:

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                'Обслуживание',
                web_app=WebAppInfo(url=URL, points=points)
            ))
        await message.answer('Приветствие', reply_markup=markup)
    else:
        await message.answer(
            'Список точек не передан, нажмите "/start" ещё раз'
        )


@dp.message_handler(content_types=['web_app_data'])
async def web_app(message: types.Message):
    data = json.loads(message.web_app_data.data)
    data['user'] = message.from_user.username
    append_in_table(data)
    data['date'] = str(datetime.now())[:19]
    await message.answer(data)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    executor.start_polling(dp)
