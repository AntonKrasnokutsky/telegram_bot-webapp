import json
import logging
import requests
import sys
from http import HTTPStatus

from exceptions import (
    AnyError,
    ExternalCompanyExistError,
    PontExistError,
    ServiceInfoExistError,
    ServiceManUnregisteredError
)

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


class AuthAPI():
    def __init__(self, *args, **kwargs):
        self.__api_token = ''
        self.headers = {"Authorization": f"Token {self.__api_token}"}
        self.__URL_API_AUTH = kwargs['url_api_auth']
        self.__AUTH = {
            'username': kwargs['user'],
            'password': kwargs['password'],
        }

    def get_token(self, *args, **kwargs):
        response = requests.post(self.__URL_API_AUTH, data=self.__AUTH)
        if response.status_code == HTTPStatus.OK:
            logging.info('Обновление токена')
            self.__api_token = json.loads(response.text)['auth_token']
            self.headers = {"Authorization": f"Token {self.__api_token}"}
        logging.info(f'Обновление токена. Status: {response.status_code}')
        if response.status_code != HTTPStatus.OK:
            logging.info(f'Обновление токена. Status: {response.text}')
        return response.status_code


class ServiceMan():
    def __init__(self, *args, **kwargs):
        self.__URL_API_SERVICE_MAN = kwargs['url_api_service_man']

    def __get_api_services_man(self, user_id, auth_api: AuthAPI, **kwargs):
        return requests.get(
            self.__URL_API_SERVICE_MAN,
            headers=auth_api.headers,
            params={'telegram_id': user_id}
        )

    def __post_api_services_man(self, body, auth_api: AuthAPI, **kwargs):
        requests.post(
            self.__URL_API_SERVICE_MAN,
            data=body,
            headers=auth_api.headers
        )

    def user(self, user_id, auth_api: AuthAPI):
        logging.debug('Получеие списка инженеров.')
        response = self.__get_api_services_man(user_id, auth_api)
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            auth_api.get_token()
            response = self.__get_api_services_man(user_id, auth_api)
        return json.loads(response.text)

    def check_user(self, user_id, auth_api: AuthAPI):
        response = self.__get_api_services_man(user_id, auth_api)
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            auth_api.get_token()
            self.__get_api_services_man(user_id, auth_api)
        try:
            response_json = json.loads(response.text)[0]
        except IndexError:
            return False

        return response_json['activ']

    def service_man_get_id(self, telegram_id, auth_api: AuthAPI):
        response = self.__get_api_services_man(telegram_id, auth_api)
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            auth_api.get_token()
            response = self.__get_api_services_man(telegram_id, auth_api)
        try:
            response_json = json.loads(response.text)[0]
        except IndexError:
            return False

        return response_json.get('id', False)

    def service_man_change_activ(self, service_man_id, auth_api: AuthAPI):
        url = f'{self.__URL_API_SERVICE_MAN}{service_man_id}/change_activ/'
        response = requests.post(
            url,
            headers=auth_api.headers
        )
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            auth_api.get_token()
            response = requests.post(
                url,
                headers=auth_api.headers
            )
        if response.status_code == HTTPStatus.OK:
            return json.loads(response.text)

        return False

    def registr_man(self, user, auth_api: AuthAPI):
        body = {
            'name': user['name'],
            'telegram_id': user['telegram_id'],
            'activ': True
        }
        response = self.__post_api_services_man(body, auth_api)
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            auth_api.get_token()
            response = self.__post_api_services_man(body, auth_api)
        if response.status_code == HTTPStatus.CREATED:
            return json.loads(response.text)
        return False


class Service():
    def __init__(self, *args, **kwargs):
        self.__URL_API_SERVICE = kwargs['url_api_service']

    def __request_api_service(self, body, auth_api: AuthAPI):
        return requests.post(
            self.__URL_API_SERVICE,
            data=body,
            headers=auth_api.headers
        )

    def send_service_info(self, data: dict, auth_api: AuthAPI):
        body = {
            'date': data['date'],
            'serviceman': data['fio'],
            'point': data['point'],
            'collection': data['collection'],
            'coffee': data['coffee'],
            'mokko': data['mokko'],
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
            'straws': data['straws'],
            'fuelcompensation': data['fuel'],
        }
        response = self.__request_api_service(body, auth_api)
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            logging.info('Требуется обновление токена')
            auth_api.get_token()
            response = self.__request_api_service(body, auth_api)

        if response.status_code == HTTPStatus.CREATED:
            return
        try:
            response_json = json.loads(response.text)
            response_text = list(map(str, response_json))[0]
        except json.decoder.JSONDecodeError:
            response_text = response.text
        match response_text:
            case 'serviceman':
                raise ServiceManUnregisteredError(
                    'Не зарегистрирован'
                )
            case 'service_exist':
                raise ServiceInfoExistError(
                    'Уже сохранено'
                )
            case 'point_not_exist':
                raise PontExistError(
                    'Обновите список точек.'
                )
            case _:
                raise AnyError(
                    response.text
                )


class Repair():
    def __init__(self, *args, **kwargs):
        self.__URL_API_REPAIR = kwargs['url_api_repair']

    def __request_api_repair(self, body, auth_api: AuthAPI):
        return requests.post(
            self.__URL_API_REPAIR,
            data=body,
            headers=auth_api.headers
        )

    def send_repairs_info(self, data: dict, auth_api: AuthAPI):
        body = {
            'date': data['date'],
            'serviceman': data['fio'],
            'point': data['point'],
            'fuelcompensation': data['fuel'],
            'comments': data['description'],
        }
        try:
            body['typework'] = data['types_work']
        except KeyError:
            pass
        response = self.__request_api_repair(body, auth_api)
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            logging.info('Требуется обновление токена')
            auth_api.get_token()
            response = self.__request_api_repair(body, auth_api)
        if response.status_code == HTTPStatus.CREATED:
            return
        response_json = json.loads(response.text)
        response_text = list(map(str, response_json))[0]
        match response_text:
            case 'serviceman':
                raise ServiceManUnregisteredError(
                    'Не зарегистрирован'
                )
            case 'repair_exist':
                raise ServiceInfoExistError(
                    'Уже сохранено'
                )
            case 'point_not_exist':
                raise PontExistError(
                    'Обновите список точек.'
                )
            case _:
                raise AnyError(
                    response.text
                )


class Audit():
    def __init__(self, *args, **kwargs):
        self.__URL_API = kwargs['url_api_audit']

    def __request_api(self, body, auth_api: AuthAPI):
        return requests.post(
            self.__URL_API,
            data=body,
            headers=auth_api.headers
        )

    def send_info(self, data: dict, auth_api: AuthAPI):
        body = {
            'date': data['date'],
            'serviceman': data['fio'],
            'coffee': data['coffee'],
            'mokko': data['mokko'],
            'cream': data['cream'],
            'chocolate': data['chocolate'],
            'raf': data['raf'],
            'sugar': data['sugar'],
            'syrup_caramel': data['syrup_caramel'],
            'syrup_nut': data['syrup_nut'],
            'glasses': data['glasses'],
            'covers': data['covers'],
            'stirrer': data['stirrer'],
            'straws': data['straws'],
        }
        try:
            body['typework'] = data['types_work']
        except KeyError:
            pass
        response = self.__request_api(body, auth_api)
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            logging.info('Требуется обновление токена')
            auth_api.get_token()
            response = self.__request_api(body, auth_api)
        if response.status_code == HTTPStatus.CREATED:
            return
        response_json = json.loads(response.text)
        response_text = list(map(str, response_json))[0]
        match response_text:
            case 'serviceman':
                raise ServiceManUnregisteredError(
                    'Не зарегистрирован'
                )
            case _:
                raise AnyError(
                    response.text
                )


# Ремонт оборудования сторонних компаний
class ExternalRepair():
    def __init__(self, *args, **kwargs):
        self.__URL_API_EXTERNAL_REPAIR = kwargs['url_api']
        self.__URL_API_EXTERNAL_REPAIR_SALARY = kwargs['url_api_salary']

    def __request_api_external_repair(self, body, auth_api: AuthAPI):
        return requests.post(
            self.__URL_API_EXTERNAL_REPAIR,
            data=body,
            headers=auth_api.headers
        )

    def __request_api_salary(self, params, auth_api: AuthAPI):
        return requests.get(
            self.__URL_API_EXTERNAL_REPAIR_SALARY,
            headers=auth_api.headers,
            params=params
        )

    def send_extenal_repairs_info(self, data: dict, auth_api: AuthAPI):
        body = {
            'date': data['date'],
            'serviceman': data['fio'],
            'company': data['company'],
            'comment': data['comment'],
        }
        try:
            body['typework'] = data['types_work']
        except KeyError:
            pass
        response = self.__request_api_external_repair(body, auth_api)
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            logging.info('Требуется обновление токена')
            auth_api.get_token()
            response = self.__request_api_repair(body, auth_api)
        if response.status_code == HTTPStatus.CREATED:
            return
        response_json = json.loads(response.text)
        response_text = list(map(str, response_json))[0]
        match response_text:
            case 'serviceman':
                raise ServiceManUnregisteredError(
                    'Не зарегистрирован'
                )
            case 'repair_exist':
                raise ServiceInfoExistError(
                    'Уже сохранено'
                )
            case 'company_not_exist':
                raise ExternalCompanyExistError(
                    'Обновите список точек.'
                )
            case _:
                raise AnyError(
                    response.text
                )

    def get_salary(
        self,
        auth_api,
        service_man=None,
        date_after=None,
        date_before=None
    ):
        params = {
            'date_after': date_after,
            'date_before': date_before,
            'service_man': service_man,
        }
        response = self.__request_api_salary(params, auth_api)
        response_json = json.loads(response.text)
        return response_json['salary']
