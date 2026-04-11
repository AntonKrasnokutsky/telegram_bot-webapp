import json
import os
import requests
import time
from http import HTTPStatus

import requests_api

from datetime import datetime, timedelta
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


load_dotenv()

URL_MAIN = os.getenv("URL_MAIN")
URL_VENDING_MACHINES_LIST = os.getenv("URL_VENDING_MACHINES_LIST")
URL_VENDING_MACHINES = os.getenv("URL_VENDING_MACHINES")
LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")

datetime_format_string = "%d.%m.%Y"

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(2)

# Авторизация для API
auth_api = requests_api.AuthAPI(
    url_api_auth=os.getenv('URL_API_AUTH'),
    user=os.getenv('API_USER'),
    password=os.getenv('API_PASSWORD'),
)
# Список игнорируемых событий
exclude_events = []

def auth():
    driver.get(URL_MAIN)

    input_login_box = driver.find_element(By.NAME, "Login")
    input_login_box.send_keys(LOGIN)
    input_password_box = driver.find_element(By.NAME, "Password")
    input_password_box.send_keys(PASSWORD)
    input_password_box.submit()


def vending_machines_list_page():
    driver.get(URL_VENDING_MACHINES_LIST)


def parsing():
    vending_machines_list = []

    ls = driver.find_element(By.XPATH, '/html/body/table[5]')
    rows = ls.find_elements(By.XPATH, './/tr')
    for row in rows[1:]:
        # Получаем название точки из третьего столбца
        tds = row.find_element(By.XPATH, './/td[3]')
        name = tds.text
        ind_name = name.rfind(' ')
        # получаем ссылку из вотрого столбца
        link = row.find_element(
            By.XPATH,
            ".//td[2]/a[contains(@href,'/n/vmc.html?')]"
        )
        href = link.get_attribute('href')
        ind = href.index("?") + 1
        vending_machines_list.append({
            "url": f"{URL_VENDING_MACHINES}{href[ind:]}#cur",
            "name": name[:ind_name].rstrip(),
        })
    parsing_logs(vending_machines_list)


def parsing_logs(vending_machines_list):
    for vending_machine in vending_machines_list:
        logs = {
            "point": vending_machine["name"],
            "events": [],
        }
        events_parse = {
                datetime.now().date(): {},
                datetime.now().date() - timedelta(days=1): {},
            }
        driver.get(vending_machine["url"])
        rows = driver.find_elements(By.XPATH, "/html/body/table[3]/tbody/tr")
        for row in rows[1:]:
            cells = row.find_elements(By.XPATH, ".//td")
            if not (cells[2].text in exclude_events):
                dt = datetime.strptime(cells[1].text[:10], datetime_format_string)
                if (dt.date() == datetime.now().date()
                or dt.date() == datetime.now().date() - timedelta(days=1)):
                    try:
                        events_parse[dt.date()][cells[2].text] += 1
                    except KeyError:
                        events_parse[dt.date()][cells[2].text] = 1
        for date in events_parse.keys():
            for key, count in events_parse[date].items():
                logs["events"].append({'date': str(date), 'event': key, 'count': count})
        url_events = 'http://localhost:8000/api/v2/parse_events/events_of_points/'
        response = requests.post(
            url_events,
            json = logs,
            headers=auth_api.headers,
        )

        print(json.loads(response.text))
        # print(vending_machine["name"])
        #     # for ivent in 
        print(logs)


def get_exclude_events():
    url_events = 'http://localhost:8000/api/v2/parse_events/events/'
    response = requests.get(
        url_events,
        headers=auth_api.headers,
    )
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        auth_api.get_token()
        response = requests.get(
            url_events,
            headers=auth_api.headers,
        )
    events = json.loads(response.text)
    
    for event in events:
        exclude_events.append(event['event'])
    # url_events = 'http://localhost:8000/api/v2/parse_events/events_of_points/'
    # response = requests.post(
    #     url_events,
    #     # data={'count': 4, 'date': '2025-10-31', 'event': 3},
    #     json = {'events': [{'count': 4, 'date': '2025-10-31', 'event': 'Событие 1'}, {'count': 467, 'date': '2025-10-31', 'event': 'Событие 2'}], 'point': 'РоКсКБС--Усть-Донецкий Строителей 72 Будка /:Зодиак:/ =тд270= 26.09.25 (:СО-АВ:)'},
    #                                                                                                                                                        'РоКсКБС--Усть-Донецкий Строителей 72 Будка /:Зодиак:/ =тд270= 26.09.25 (:СО-АВ:)'
    #     headers=auth_api.headers,
    # )
    # print(json.loads(response.text))




if __name__ == "__main__":
    start_time = time.time()  # запоминаем время начала выполнения функции
    
    auth_api.get_token()
    get_exclude_events()
    auth()
    vending_machines_list_page()
    parsing()
    driver.quit()

    end_time = time.time()  # запоминаем время окончания выполнения функции

    execution_time = end_time - start_time  # вычисляем время выполнения функции
    print(f"Время выполнения функции: {execution_time} секунд")
