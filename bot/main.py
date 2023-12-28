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
    logging.debug('Получеие списка инженеров.')
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
            data['syrup_caramel'],
            data['syrup_nut'],
            data['syrup_other'],
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
        logging.debug('Запуск бота. Успешное обновление точек.')
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
        logging.warning('Запуск бота. Точки не обновлены.')
        await message.answer(
            'Список точек не обновлен, нажмите "/update_points" ещё раз'
        )


@dp.message_handler(commands=['update_points'])
async def update_points(message: types.Message):
    await message.answer('Обновление списка точек, подождите.')
    response = requests.get(URL_API_POINTS)
    if response.status_code == HTTPStatus.OK:
        logging.debug('Обновление точек. Успешно.')
        await message.answer('Список точек обновлён')
    else:
        logging.warning('Обновление точек. Провал.')
        await message.answer(
            'Список точек не обновлён, нажмите "/update_points" ещё раз'
        )


@dp.message_handler(commands=['service'])
async def service(message: types.Message):
    logging.debug('Отображение кнопки "Обслуживание".')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton(
            'Обслуживание',
            web_app=WebAppInfo(url=URL_SERVICE)
        ))
    await message.answer('Обслуживание', reply_markup=markup)


@dp.message_handler(commands=['repair'])
async def repair(message: types.Message):
    logging.debug('Отображение кнопки "Ремонт".')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton(
            'Ремонт',
            web_app=WebAppInfo(url=URL_REPAIR)
        ))
    await message.answer('Ремонт', reply_markup=markup)


def make_messagedata(data, *args, **kwargs):
    logging.debug('Подготовка ответного сообщения.')
    result = ''
    result += f'Вид работ: {data["type"]}\n'
    result += f'Инженер: {data["fio"]}\n'
    result += f'Точка обслуживания: {data["point"]}\n'
    if data['type'] == 'Обслуживание':
        result += f'Инкачация: ₽\xa0 {data["collection"]}\n'
        result += f'Кофе: {data["coffee"]}\n'
        result += f'Сливки: {data["cream"]}\n'
        result += f'Шоколад: {data["chocolate"]}\n'
        result += f'Раф: {data["raf"]}\n'
        result += f'Сахар: {data["sugar"]}\n'
        result += f'Сироп "Солёная карамель": {data["syrup_caramel"]}\n'
        result += f'Сироп "Лесной орех": {data["syrup_nut"]}\n'
        result += f'Сироп "Другой": {data["syrup_other"]}\n'
        result += f'Стаканы: {data["glasses"]}\n'
        result += f'Крышки: {data["covers"]}\n'
        result += f'Размешиватели: {data["stirrer"]}\n'
        result += f'Трубочки: {data["straws"]}'
    elif data['type'] == 'Ремонт':
        result += f'Категория: {data["category"]}\n'
        result += f'Замена: {data["repair"]}\n'
        result += f'Комментарий: {data["description"]}'
    return result


@dp.message_handler(content_types=['web_app_data'])
async def web_app(message: types.Message):
    logging.debug('WebApp.')
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
    data['syrup_caramel'] = 1 if data['syrup_caramel'] else 0
    data['syrup_nut'] = 1 if data['syrup_nut'] else 0
    data['syrup_other'] = 1 if data['syrup_other'] else 0
    if data['type'] == 'service':
        logging.debug('Данны по обслжуиванию.')
        data['type'] = 'Обслуживание'
        append_service_in_table(data)
    elif data['type'] == 'repair':
        logging.debug('Данны по ремонту.')
        data['type'] = 'Ремонт'
        append_repair_in_table(data)
    current_point[message.from_user.id] = (
        f'Вид работ: {data["type"]}\n'
        f'Точка: {data["point"]}\n'
        f'Инженер: {data["fio"]}'
    )
    # message_data = make_messagedata(data)
    logging.debug('Отправка сообщения с инфораацией о выполненной работе.')
    await message.answer(make_messagedata(data))


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def forward_photo(message: types.Message):
    logging.debug('Пересылка фотографии.')
    await bot.send_photo(
        chat_id=CHAT_ID,
        photo=message.photo[-1].file_id,
        caption=current_point[message.from_user.id]
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    executor.start_polling(dp)
