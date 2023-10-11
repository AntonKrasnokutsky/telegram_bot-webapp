# import base64
import shutil
import httplib2
import json
import requests
import os
from datetime import datetime, timezone
from http import HTTPStatus
# from io import BytesIO
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
URL_API_PHOTO = os.getenv('URL_API_PHOTO')
bot = Bot(TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
SHEET_SERVICE = os.getenv('SHEET_SERVICE')
SHEET_REPEAR = os.getenv('SHEET_REPEAR')
POINTS_RANGE = os.getenv('POINTS_RANGE')
SERVICEMAN_RANGE = os.getenv('SERVICEMAN_RANGE')


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
            f'₽\xa0{data["collection"]}',
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
            '',
            '',
            '',
            '',
            '',
            'photo'
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
    points = {
        'names': get_list_points()
    }
    response = requests.post(URL_API_POINTS, json=json.dumps(points))
    if response.status_code == HTTPStatus.CREATED:

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
            'Список точек не передан, нажмите "/start" ещё раз'
        )


@dp.message_handler(commands=['update_points'])
async def update_points(message: types.Message):
    await message.answer('Обновление списка точек, подождите.')
    points = {
        'names': get_list_points()
    }
    response = requests.post(URL_API_POINTS, json=json.dumps(points))
    if response.status_code == HTTPStatus.CREATED:
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
    for user in users:
        if message.from_user.username == user[2]:
            data['email'] = user[0]
            data['fio'] = user[1]
            break
    date_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
    tz = datetime.strptime('+0300', '%z').tzinfo
    date_msk = date_utc.astimezone(tz)
    data['date'] = date_msk.strftime("%d.%m.%Y %H:%M:%S")
    if data['type'] == 'service':
        append_service_in_table(data)
    elif data['type'] == 'repair':
        append_repair_in_table(data)
    await message.answer(data)
    if len(data['photo']):
        # photos = []
        for name in data['photo']:
            result = requests.get(URL_API_PHOTO + name)
            print(result.text)
            if (result.text not in [
                    'Ошибка файла',
                    'Неподдерживаемый тип запроса']
                    and result.status_code == HTTPStatus.OK):
                if result.status_code == HTTPStatus.OK:
                    file = os.path.join(BASE_DIR, 'photo', name)
                    with open(file, 'wb') as photo:
                        result.raw.decode_content = True
                        shutil.copyfileobj(result.raw, photo)

                # photos.append(
                #     os.path.join(BASE_DIR, 'photo', name)
                # )
                # with open(photos[-1], 'wb') as photo:
                #     photo.write(result.text)
                await bot.send_photo(chat_id=message.chat.id, photo=photo)

            else:
                await message.answer('Проблема с фото')
            # with open(f'photo/{name}', 'wb') as photo:
            #     photo.write(requests.get(URL_API_PHOTO + name).content)

            # photos.append(
            #    BytesIO(requests.get(URL_API_PHOTO + name).content)
            # )
            # await bot.send_photo(chat_id=message.chat.id, photo=photos[-1])


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    result = requests.get(URL_API_PHOTO + 'photo1.jpeg')
    print(result.text)
    if result.status_code == HTTPStatus.OK:
        if result.status_code == HTTPStatus.OK:
            file = os.path.join(BASE_DIR, 'photo', 'photo1.jpeg')
            with open(file, 'wb') as photo:
                result.raw.decode_content = True
                shutil.copyfileobj(result.raw, photo)

    executor.start_polling(dp)
