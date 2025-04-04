import json
import logging
import os
import sys
from datetime import datetime, timezone
from http import HTTPStatus

import buttons
import requests
import requests_api
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
from exceptions import (
    AnyError,
    ExternalCompanyExistError,
    PontExistError,
    ServiceInfoExistError,
    ServiceManUnregisteredError
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
URL_API_POINTS = os.getenv('URL_API_POINTS')
CHAT_ID = os.getenv('CHAT_ID')
REPAIR_CHAT_ID = os.getenv('REPAIR_CHAT_ID')
AUDIT_CHAT_ID = os.getenv('AUDIT_CHAT_ID')
EXTERNAL_REPAIR_CHAT_ID = os.getenv('EXTERNAL_REPAIR_CHAT_ID')
bot = Bot(TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

service_man = {
    'name': '',
    'telegram_id': 0,
    'create': False,
    'change_activ': False
}

reg_service_man = {}
current_point = {}
current_company = {}


def update_points(*args, **kwargs):
    response = requests.get(URL_API_POINTS, headers=auth_api.headers)
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        auth_api.get_token()
        response = requests.get(URL_API_POINTS, headers=auth_api.headers)
    if response.status_code == HTTPStatus.OK:
        logging.info('Список точек обновлен')
        return True
    logging.info(
        f'Список точек не обновлен. Status: {response.status_code}'
    )
    return False


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if user.user(message.from_user.id, auth_api)[0]['office_engineer']:
        await message.answer(
            'Бот готов к работе. Внешний',
            reply_markup=buttons.repairs_office_button,
        )
    else:
        await message.answer(
            'Бот готов к работе.',
            reply_markup=buttons.start_buttons,
        )


@dp.message_handler(commands=['update_points'])
async def update_points_command(message: types.Message):
    if not user.user(message.from_user.id, auth_api)[0]['office_engineer']:
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
    if not user.user(message.from_user.id, auth_api)[0]['office_engineer']:
        logging.debug('Отображение кнопки "Обслуживание".')
        await message.answer(
            'Обслуживание',
            reply_markup=buttons.service_button
        )


@dp.message_handler(commands=['repair'])
async def repair(message: types.Message):
    if not user.user(message.from_user.id, auth_api)[0]['office_engineer']:
        logging.debug('Отображение кнопки "Ремонт".')
        await message.answer('Ремонт', reply_markup=buttons.repair_button)


@dp.message_handler(commands=['change_activ'])
async def change_activ(message: types.Message):
    if user.check_user(message.from_user.id, auth_api):
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
    if user.check_user(message.from_user.id, auth_api):
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


@dp.message_handler(commands=['Зарплата'])
async def salary(message: types.Message):
    service_man = user.user(message.from_user.id, auth_api)[0]
    if service_man['office_engineer']:
        await message.answer(
            'Информация о зарлате',
            reply_markup=buttons.repairs_office_button_salary,
        )


@dp.message_handler(commands=['all_time'])
async def salary_all_time(message: types.Message):
    service_man = user.user(message.from_user.id, auth_api)[0]
    if service_man['office_engineer']:
        salary_result = external_repairs.get_salary(
            auth_api,
            service_man=service_man['id']
        )
        answer = f'Заработано {salary_result} р.'
        await message.answer(answer)


async def service_man_change(message: types.Message):
    reg_service_man[message.from_user.id]['change_activ'] = False
    try:
        telegram_id = int(message.text)
    except ValueError:
        logging.info(
            'Изменение статуса сотрудника. Не верный Telegram ID'
        )
        return
    service_man_id = user.service_man_get_id(telegram_id, auth_api)
    logging.info(
        'Изменение статуса сотрудника.'
    )
    if service_man_id:
        service_man_after_change = user.service_man_change_activ(
            service_man_id,
            auth_api,
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
        registr = user.registr_man(reg_service_man[user_id])
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
    user_id = message.from_user.id
    if reg_service_man.get(user_id, False):
        if (
            user.check_user(user_id, auth_api)
            and reg_service_man[user_id].get(
                'change_activ',
                False
            )
        ):
            await service_man_change(message)
        elif (
            user.check_user(user_id, auth_api)
            and reg_service_man[user_id].get(
                'create',
                False
            )
        ):
            await registr_service_man(message)


def make_messagedata(data, *args, **kwargs):
    logging.debug('Подготовка ответного сообщения.')
    work_type = [
        'Обслуживание',
        'Ремонт',
    ]
    external_work_type = [
        'Ремонт для внешних',
    ]
    result = ''
    result += f'Вид работ: {data["type"]}\n'
    result += f'Инженер: {data["fio"]}\n'
    if data['type'] in work_type:
        result += f'Точка обслуживания: {data["point"]}\n'
    if data['type'] in external_work_type:
        result += f'Обслуживаемая компания: {data["company"]}\n'
    if data['type'] == 'Обслуживание':
        result += f'Инкасация: ₽\xa0 {data["collection"]}\n'
        result += f'Кофе: {data["coffee"]}\n'
        result += f'Мокко: {data["mokko"]}\n'
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
        try:
            result += f'Виды работ: {data["types_work"]}\n'
        except KeyError:
            pass
        result += f'Компенсация ГСМ: {data["fuel"]}\n'
        result += f'Комментарий: {data["description"]}'
    elif data['type'] == 'Ревизия':
        result += f'01. Кофе зерно: {data["coffee"]}\n'
        result += f'01. Мокко: {data["mokko"]}\n'
        result += (
            '02. Заменитель сухих сливок Aristocrat "Топпинг" 1000г '
            f'(8 шт. в коробке): {data["cream"]}\n'
        )
        result += (
            '03. Горячий шоколад Aristocrat Классический 1000г '
            f'(12 шт. в коробке): {data["chocolate"]}\n'
        )
        result += (
            '04. Смесь сухая "Rapf-coffe" со вкусом кокоса 1000г '
            f'(12 шт. в коробке): {data["raf"]}\n'
        )
        result += (
            '05. Сахар порционный 5 г. BLACK (500 шт./кор - 2500 г.): '
            f'{data["sugar"]}\n'
        )
        result += f'06. Стакан 350 мл. черный (50 шт/уп.): {data["glasses"]}\n'
        result += f'07. Крышка для стакана (100 шт./уп.): {data["covers"]}\n'
        result += (
            '08. Трубочки коктейльные черные прямые 2*210 '
            f'(1000 шт./упак): {data["straws"]}'
        )
        result += (
            '09. Размешиватель деревянный 18 см. '
            f'(250 шт./упак): {data["stirrer"]}\n'
        )
        result += (
            '10. Сироп "Соленая карамель" (пл. 1л.)": '
            f'{data["syrup_caramel"]}\n'
        )
        result += f'11. Сироп "Лесной орех" (пл. 1л.): {data["syrup_nut"]}\n'
    elif data['type'] == 'Ремонт для внешних':
        result += 'Виды работ:'
        for work in data["types_work"]:
            result += (
                f'{work["external_work"]} '
                f'в количестве {work["count"]}\n'
            )
        result += f'Коментарий: {data["comment"]}\n'
        result += f'Серийный номер кофе: {data["serial_num_coffe"]}'
    return result


def user_data(user_id, data):
    users = user.user(user_id, auth_api)
    data['fio'] = users[0]['name']


async def web_app_service(message: types.Message, data):
    logging.debug('Данны по обслжуиванию.')
    data['syrup_caramel'] = 1 if data['syrup_caramel'] else 0
    data['syrup_nut'] = 1 if data['syrup_nut'] else 0
    data['syrup_other'] = 1 if data['syrup_other'] else 0
    data['type'] = 'Обслуживание'
    data['fio'] = message.from_user.id
    try:
        services.send_service_info(data, auth_api)
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
        answer = 'Данные об обслуживании точки сегодня уже были сохранены'
        logging.info(answer)
        await message.answer(answer)
        return
    except PontExistError:
        answer = 'Неизвестная точка, обновте список точек'
        logging.info(answer)
        await message.answer(answer)
        return
    except AnyError as e:
        answer = f'Данные не сохранены. Ответ сервера: {e.args}'
        logging.info(answer)
        await message.answer(answer)
        return

    user_data(message.from_user.id, data)
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


async def web_app_repairs(message: types.Message, data):
    logging.debug('Данные по ремонту.')
    data['type'] = 'Ремонт'
    data['fio'] = message.from_user.id
    try:
        repairs.send_repairs_info(data, auth_api)
        logging.info('Данные по ремоту отправлены.')
    except ServiceManUnregisteredError:
        answer = (
            'Попытка внести данные незарегистрированным '
            f'инженером: @{message.from_user.username}'
        )
        logging.critical(answer)
        await bot.send_message(
            chat_id=REPAIR_CHAT_ID,
            text=answer
        )
        await message.answer('Данные не сохранены')
        return
    except ServiceInfoExistError:
        answer = 'Данные о ремонте точки сегодня уже были сохранены'
        logging.info(answer)
        await message.answer(answer)
        return
    except PontExistError:
        answer = 'Неизвестная точка, обновите список точек'
        logging.info(answer)
        await message.answer(answer)
        return
    except AnyError as e:
        answer = f'Данные не сохранены. Ответ сервера: {e.args}'
        return

    user_data(message.from_user.id, data)
    current_point[message.from_user.id] = (
        f'Вид работ: {data["type"]}\n'
        f'Точка: {data["point"]}\n'
        f'Инженер: {data["fio"]}'
    )
    logging.debug('Отправка сообщения с инфораацией о выполненной работе.')
    answer = make_messagedata(data)
    await message.answer(answer)
    await bot.send_message(
        chat_id=REPAIR_CHAT_ID,
        text=answer
    )


async def web_app_audit(message: types.Message, data):
    logging.debug('Данны по ревизии.')
    data['type'] = 'Ревизия'
    data['fio'] = message.from_user.id
    try:
        audit.send_info(data, auth_api)
        logging.info('Данные по ревизии отправлены.')
    except ServiceManUnregisteredError:
        answer = (
            'Попытка внести данные незарегистрированным '
            f'инженером: @{message.from_user.username}'
        )
        logging.critical(answer)
        await bot.send_message(
            chat_id=AUDIT_CHAT_ID,
            text=answer
        )
        await message.answer('Данные не сохранены')
        return
    except AnyError as e:
        answer = f'Данные не сохранены. Ответ сервера: {e.args}'
        logging.info(answer)
        await message.answer(answer)
        return

    user_data(message.from_user.id, data)
    current_point[message.from_user.id] = (
        f'Вид работ: {data["type"]}\n'
        f'Инженер: {data["fio"]}'
    )
    logging.debug('Отправка сообщения с информацией о ревизии.')
    answer = make_messagedata(data)
    await message.answer(answer)
    await bot.send_message(
        chat_id=AUDIT_CHAT_ID,
        text=answer
    )


async def web_app_external_repair(message: types.Message, data):
    logging.debug('Данные по внешнему ремонту.')
    data['type'] = 'Ремонт для внешних'
    data['fio'] = message.from_user.id
    try:
        external_repairs.send_extenal_repairs_info(data, auth_api)
        logging.info('Данные по ремоту внешних компаний отправлены.')
    except ServiceManUnregisteredError:
        answer = (
            'Попытка внести данные незарегистрированным '
            f'инженером: @{message.from_user.username}'
        )
        logging.critical(answer)
        await bot.send_message(
            chat_id=REPAIR_CHAT_ID,
            text=answer
        )
        await message.answer('Данные не сохранены')
        return
    except ExternalCompanyExistError:
        answer = 'Неизвестная компания'
        logging.info(answer)
        await message.answer(answer)
        return
    except AnyError as e:
        answer = f'Данные не сохранены. Ответ сервера: {e.args}'
        return

    user_data(message.from_user.id, data)
    current_company[message.from_user.id] = (
        f'Вид работ: {data["type"]}\n'
        f'Компания: {data["company"]}\n'
        f'Инженер: {data["fio"]}'
    )
    logging.debug(
        'Отправка сообщения с инфораацией о выполненной работе. '
        'По внешним компаниям.'
    )
    answer = make_messagedata(data)
    await message.answer(answer)
    await bot.send_message(
        chat_id=EXTERNAL_REPAIR_CHAT_ID,
        text=answer
    )


async def web_app_salary(message: types.Message, data):
    user_id = message.from_user.id
    service_man = user.user(user_id, auth_api)[0]
    if service_man['office_engineer']:
        salary_result = external_repairs.get_salary(
            auth_api,
            service_man=service_man['id'],
            date_after=data['date_after'],
            date_before=data['date_before'],
        )
        answer = f'Заработано {salary_result} р.'

        await message.answer(
            answer,
            reply_markup=buttons.repairs_office_button,
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
    if data['type'] in ['service', 'repair', 'external_repair']:
        data['date'] = date_msk.strftime("%d.%m.%Y %H:%M:%S")
    else:
        data['date'] = date_msk.strftime("%d.%m.%Y")
    if data['type'] == 'service':
        await web_app_service(message, data)
    elif data['type'] == 'repair':
        await web_app_repairs(message, data)
    elif data['type'] == 'audit':
        await web_app_audit(message, data)
    elif data['type'] == 'external_repair':
        await web_app_external_repair(message, data)
    elif data['type'] == 'salary':
        await web_app_salary(message, data)


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def forward_photo(message: types.Message):
    logging.debug('Пересылка фотографии.')
    if current_point.get(message.from_user.id, False):
        if 'Обслуживание' in current_point[message.from_user.id]:
            await bot.send_photo(
                chat_id=CHAT_ID,
                photo=message.photo[-1].file_id,
                caption=current_point[message.from_user.id]
            )
        if 'Ремонт' in current_point[message.from_user.id]:
            await bot.send_photo(
                chat_id=REPAIR_CHAT_ID,
                photo=message.photo[-1].file_id,
                caption=current_point[message.from_user.id]
            )
    elif current_company.get(message.from_user.id, False):
        await bot.send_photo(
            chat_id=EXTERNAL_REPAIR_CHAT_ID,
            photo=message.photo[-1].file_id,
            caption=current_company[message.from_user.id]
        )
    else:
        await message.answer('Сначала нужно внести данные об обслуживании.')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    auth_api = requests_api.AuthAPI(
        url_api_auth=os.getenv('URL_API_AUTH'),
        user=os.getenv('API_USER'),
        password=os.getenv('API_PASSWORD'),
    )
    auth_api.get_token()

    user = requests_api.ServiceMan(
        url_api_service_man=os.getenv('URL_API_SERVICE_MAN')
    )

    services = requests_api.Service(
        url_api_service=os.getenv('URL_API_SERVICE')
    )
    repairs = requests_api.Repair(
        url_api_repair=os.getenv('URL_API_REPAIR')
    )
    audit = requests_api.Audit(
        url_api_audit=os.getenv('URL_API_AUDIT')
    )
    external_repairs = requests_api.ExternalRepair(
        url_api=os.getenv('URL_API_EXTERNAL_REPAIR'),
        url_api_salary=os.getenv('URL_API_EXTERNAL_REPAIR_SALARY')
    )
    executor.start_polling(dp)
