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

from exceptions import (
    AnyError,
    ServiceInfoExistError,
    ServiceManUnregisteredError
)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
URL_SERVICE = os.getenv('URL_SERVICE')
URL_REPAIR = os.getenv('URL_REPAIR')
URL_API_POINTS = os.getenv('URL_API_POINTS')
URL_API_SERVICE = os.getenv('URL_API_SERVICE')
URL_API_AUTH = os.getenv('URL_API_AUTH')
URL_API_SERVICE_MAN = os.getenv('URL_API_SERVICE_MAN')
AUTH = {
    'username': os.getenv('API_USER'),
    'password': os.getenv('API_PASSWORD')
}
CHAT_ID = os.getenv('CHAT_ID')
bot = Bot(TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)
api_token = ''
headers = {"Authorization": f"Token {api_token}"}

CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')    # удалит при отключении google
SHEET_SERVICE = os.getenv('SHEET_SERVICE')  # удалит при отключении google
SHEET_REPEAR = os.getenv('SHEET_REPEAR')    # удалит при отключении google


service_man = {
    'name': '',
    'telegram_id': 0,
    'create': False,
    'change_activ': False
}

reg_service_man = {}
current_point = {}


def get_service_sacc():
    creds_json = os.path.dirname(__file__) + '/' + CREDENTIALS_FILE
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    creds_service = ServiceAccountCredentials.from_json_keyfile_name(
        creds_json,
        scopes
    ).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)


def requst_api_services_man(*args, **kwargs):
    return requests.get(
        URL_API_SERVICE_MAN,
        headers=headers
    )


def get_user_list():
    logging.debug('Получеие списка инженеров.')
    response = requst_api_services_man()
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        get_token()
        response = requst_api_services_man()
    return json.loads(response.text)


def get_token(*args, **kwargs):
    global api_token
    global headers
    response = requests.post(URL_API_AUTH, data=AUTH)
    if response.status_code == HTTPStatus.OK:
        logging.info('Обновление токена')
        api_token = json.loads(response.text)['auth_token']
        headers = {"Authorization": f"Token {api_token}"}
    logging.info(f'Обновление токена. Status: {response.status_code}')
    if response.status_code != HTTPStatus.OK:
        logging.info(f'Обновление токена. Status: {response.text}')
    return response.status_code


def request_api_service(body, *args, **kwargs):
    return requests.post(URL_API_SERVICE, data=body, headers=headers)


def send_service_info(data: dict, *args, **kwargs):
    body = {
        'date': data['date'],
        'serviceman': data['fio'],
        'point': data['point'],
        'collection': data['collection'],
        'coffee': data['coffee'],
        'cream': data['cream'],
        'chocolate': data['chocolate'],
        'raf': data['raf'],
        'sugar': data['sugar'],
        'syrupcaramel': data['syrup_caramel'],
        'syrupnut': data['syrup_nut'],
        'syrupother': data['syrup_other'],
        'glasses': data['glasses'],
        'covers': data['covers'],
        'stirrer': data['stirrer'],
        'straws': data['straws']
    }
    response = request_api_service(body)
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        logging.info('Требуется обновление токена')
        get_token()
        response = request_api_service(body)

    if response.status_code == HTTPStatus.OK:
        return
    response_json = json.loads(response.text)
    response_text = list(map(str, response_json))[0]
    match response_text:
        case 'serviceman':
            raise ServiceManUnregisteredError(
                'Не зарегистрирован'
            )
        case 'service_exist':
            raise ServiceInfoExistError(
                'Уже сохранено'
            )
        case _:
            raise AnyError(
                response.text
            )


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


def update_points(*args, **kwargs):
    response = requests.get(URL_API_POINTS, headers=headers)
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        get_token()
        response = requests.get(URL_API_POINTS, headers=headers)
    if response.status_code == HTTPStatus.OK:
        logging.info('Список точек обновлен')
        return True
    logging.info(
        f'Список точек не обновлен. Status: {response.status_code}'
    )
    return False


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Запуск бота.')
    if update_points():
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
async def update_points_command(message: types.Message):
    await message.answer('Обновление списка точек, подождите.')
    logging.debug('Обновление точек.')
    if update_points():
        await message.answer('Список точек обновлён')
    else:
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


def check_user(user_id, *args, **kwargs):
    response = requests.get(
        URL_API_SERVICE_MAN,
        headers=headers,
        params=f'telegram_id={user_id}'
    )
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        get_token()
        response = requests.get(
            URL_API_SERVICE_MAN,
            headers=headers,
            params=f'telegram_id={user_id}'
        )
    try:
        response_json = json.loads(response.text)[0]
    except IndexError:
        return False

    return response_json['activ']


@dp.message_handler(commands=['change_activ'])
async def change_activ(message: types.Message):
    if check_user(message.from_user.id):
        logging.info(
            f'Сотрудник @{message.from_user.username} запросил смену '
            'статуса сотрудника.'
        )
        if not reg_service_man.get(message.from_user.id, False):
            reg_service_man[message.from_user.id] = service_man.copy()
        reg_service_man[message.from_user.id]['change_activ'] = True
        reg_service_man[message.from_user.id]['create'] = False
        await message.answer(
            'Введите Telegram ID сотрудника, которому необходимо изменить '
            'статус'
        )


@dp.message_handler(commands=['staff'])
async def staff(message: types.Message):
    if check_user(message.from_user.id):
        logging.info(
            f'Сотрудник @{message.from_user.username} запросил регистрацию '
            'нового сотрудника.'
        )
        if not reg_service_man.get(message.from_user.id, False):
            reg_service_man[message.from_user.id] = service_man.copy()
        reg_service_man[message.from_user.id]['create'] = True
        reg_service_man[message.from_user.id]['name'] = ''
        reg_service_man[message.from_user.id]['telegram_id'] = ''

        reg_service_man[message.from_user.id]['change_activ'] = False
        await message.answer(
            'Для регистрации нового сотудника введите его имя'
        )


def service_man_get_id(telegram_id, *args, **kwargs):
    response = requests.get(
        URL_API_SERVICE_MAN,
        headers=headers,
        params=f'telegram_id={telegram_id}'
    )
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        get_token()
        response = requests.get(
            URL_API_SERVICE_MAN,
            headers=headers,
            params=f'telegram_id={telegram_id}'
        )
    try:
        response_json = json.loads(response.text)[0]
    except IndexError:
        return False

    return response_json.get('id', False)


def service_man_change_activ(service_man_id, *args, **kwargs):
    url = f'{URL_API_SERVICE_MAN}{service_man_id}/change_activ/'
    response = requests.post(
        url,
        headers=headers
    )
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        get_token()
        response = requests.post(
            url,
            headers=headers
        )
    if response.status_code == HTTPStatus.OK:
        return json.loads(response.text)

    return False


async def service_man_change(message: types.Message):
    reg_service_man[message.from_user.id]['change_activ'] = False
    try:
        telegram_id = int(message.text)
    except ValueError:
        logging.info(
            'Изменение статуса сотрудника. Не верный Telegram ID'
        )
        return
    service_man_id = service_man_get_id(telegram_id)
    logging.info(
        'Изменение статуса сотрудника.'
    )
    if service_man_id:
        service_man_after_change = service_man_change_activ(
            service_man_id
        )
        if service_man_after_change:
            if service_man_after_change['activ']:
                status = 'Работает'
            else:
                status = 'Уволен'
            answer = (
                f'Статус сотрудника {telegram_id} изменён на: {status} '
                f'сотрудником @{message.from_user.username}'
            )
            logging.info(answer)
            await message.answer(f'Статус изменен на: {status}')
            await bot.send_message(
                chat_id=CHAT_ID,
                text=answer
            )
        else:
            logging.info(
                f'Статус сотрудника {telegram_id} не изменён.'
            )
            await message.answer('Статус не изменен')
        return
    logging.info(f'Сотрудник с ID {telegram_id} не найден')
    await message.answer('Сотрудник не найден.')


def registr_man(user_id, *args, **kwargs):
    body = {
        'name': reg_service_man[user_id]['name'],
        'telegram_id': reg_service_man[user_id]['telegram_id']
    }
    response = requests.post(
        URL_API_SERVICE_MAN,
        data=body,
        headers=headers
    )
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        get_token()
        response = requests.post(
            URL_API_SERVICE_MAN,
            data=body,
            headers=headers
        )
    if response.status_code == HTTPStatus.CREATED:
        print(json.loads(response.text))
        return json.loads(response.text)
    return False


async def registr_service_man(message: types.Message):
    user_id = message.from_user.id
    if reg_service_man[user_id]['name'] == '':
        logging.info(
            f'Сотрудник @{message.from_user.username} указал имя '
            f'нового сотрудника: {message.text}'
        )
        reg_service_man[user_id]['name'] = message.text
        await message.answer('Введите telegram ID нового сотрудника')
    elif reg_service_man[user_id]['telegram_id'] == '':
        reg_service_man[user_id]['create'] = False
        try:
            reg_service_man[user_id]['telegram_id'] = int(message.text)
        except ValueError:
            logging.info(
                f'Сотрудник @{message.from_user.username} указал неверный '
                f'Telegram ID новго сотрудника: {message.text}'
            )
            reg_service_man[user_id]['create'] = False
            return
        registr = registr_man(user_id)
        if registr:
            answer = (
                f'Новый пользователь {reg_service_man[user_id]["name"]} '
                f'Telegram ID {reg_service_man[user_id]["telegram_id"]} '
                f'зарегистрирован сотрудником @{message.from_user.username}'
            )
            logging.info(answer)
            await message.answer('Пользователь зарегистрирован.')
            await bot.send_message(
                chat_id=CHAT_ID,
                text=answer
            )
            return
        logging.info('Новый пользователь не зарегистрирован')
        await message.answer('Новый пользователь не зарегистрирован')


@dp.message_handler()
async def any_message(message: types.Message):
    if reg_service_man.get(message.from_user.id, False):
        if (
            check_user(message.from_user.id)
            and reg_service_man[message.from_user.id].get(
                'change_activ',
                False
            )
        ):
            await service_man_change(message)
        elif (
            check_user(message.from_user.id)
            and reg_service_man[message.from_user.id].get(
                'create',
                False
            )
        ):
            await registr_service_man(message)


def make_messagedata(data, *args, **kwargs):
    logging.debug('Подготовка ответного сообщения.')
    result = ''
    result += f'Вид работ: {data["type"]}\n'
    result += f'Инженер: {data["fio"]}\n'
    result += f'Точка обслуживания: {data["point"]}\n'
    if data['type'] == 'Обслуживание':
        result += f'Инкасация: ₽\xa0 {data["collection"]}\n'
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


# Убрать после вступления в силу изменений API
def user_data(user_id, data):
    users = get_user_list()
    for user in users:
        if int(user_id) == int(user['telegram_id']):
            data['fio'] = user['name']
            break
# end


async def web_app_service(message: types.Message, data):
    logging.debug('Данны по обслжуиванию.')
    data['syrup_caramel'] = 1 if data['syrup_caramel'] else 0
    data['syrup_nut'] = 1 if data['syrup_nut'] else 0
    data['syrup_other'] = 1 if data['syrup_other'] else 0
    data['type'] = 'Обслуживание'
    data['fio'] = message.from_user.id
    try:
        send_service_info(data)
        logging.info('Данные по обслуживанию отправлены.')
    except ServiceManUnregisteredError:
        answer = (
            'Попытка внести данные незарегистрированным '
            f'инженером: @{message.from_user.username}'
        )
        logging.critical(answer)
        await bot.send_message(
            chat_id=CHAT_ID,
            text=answer
        )
        await message.answer('Данные не сохранены')
        return
    except ServiceInfoExistError:
        answer = 'Данные об обслуживании сегодня уже были сохранены'
        logging.info(answer)
        await message.answer(answer)
        return
    except AnyError:
        # answer = f'Данные не сохранены. Ответ сервера: {e.args}'
        pass

    # Убрать после вступления в силу изменений API
    user_data(message.from_user.id, data)
    # end
    current_point[message.from_user.id] = (
        f'Вид работ: {data["type"]}\n'
        f'Точка: {data["point"]}\n'
        f'Инженер: {data["fio"]}'
    )
    logging.debug('Отправка сообщения с инфораацией о выполненной работе.')
    answer = make_messagedata(data)
    await message.answer(answer)
    await bot.send_message(
        chat_id=CHAT_ID,
        text=answer
    )


@dp.message_handler(content_types=['web_app_data'])
async def web_app(message: types.Message):
    logging.debug('WebApp.')
    data = json.loads(message.web_app_data.data)
    data['email'] = 'Нет данных'
    data['fio'] = 'Нет данных'

    date_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
    tz = datetime.strptime('+0300', '%z').tzinfo
    date_msk = date_utc.astimezone(tz)
    data['date'] = date_msk.strftime("%d.%m.%Y %H:%M:%S")
    if data['type'] == 'service':
        await web_app_service(message, data)
    elif data['type'] == 'repair':
        logging.debug('Данны по ремонту.')
        data['type'] = 'Ремонт'
        # Убрать после вступления в силу изменений API
        user_data(message.from_user.id, data)
        # end
        append_repair_in_table(data)
        current_point[message.from_user.id] = (
            f'Вид работ: {data["type"]}\n'
            f'Точка: {data["point"]}\n'
            f'Инженер: {data["fio"]}'
        )
        logging.debug('Отправка сообщения с инфораацией о выполненной работе.')
        await message.answer(make_messagedata(data))


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def forward_photo(message: types.Message):
    logging.debug('Пересылка фотографии.')
    if current_point.get(message.from_user.id, False):
        await bot.send_photo(
            chat_id=CHAT_ID,
            photo=message.photo[-1].file_id,
            caption=current_point[message.from_user.id]
        )
    else:
        await message.answer('Сначала нужно внести данные об обслуживании.')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    executor.start_polling(dp)
