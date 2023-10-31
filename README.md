# telegram_bot-webapp
Телеграм-бот с использованием webApp.
Создан для системотизации сбора сведений о проведенных работах в таблице Google sheets, и пересылой фото-отчета в группу проверяющих

## Технология
telegram_bot-webapp использует ряд технологий:
- Python 3.11.5
- aiogram 2.25.1
- Django 4.2.6
- Google api python client 2.101.0
- Django rest framework 3.14.0


### Как запустить проект:
$${\color{red}Для \space полноценной \space работы \space запуск \space backend \space локально \space невозможен. \space Обязательно \space требуется \space сертификат \space ssl.}$$

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/AntonKrasnokutsky/telegram_bot-webapp.git
```

```
cd telegram_bot-webapp
```

Создать файл с переменными окружения для Django

```
nano .env
```
```
DB_ENGIN`
ENV=путь_к_переменным_окружения
```

```
nano bot/.env
```
```
TELEGRAM_BOT_TOKEN=токен_телеграм_бота
URL_SERVICE=https://{domain}/service/
URL_REPAIR=https://{domain}/repair/
CREDENTIALS_FILE=json_доступа_сервисного аккаунта
SPREADSHEET_ID=ID_таблицы_google
SHEET_SERVICE=страница_сохранения_данных_обслуживания
SHEET_REPEAR=страница_сохранения_данных_ремонта
URL_API_POINTS=https://{domain}/api/points/
POINTS_RANGE=Страница_и_диапазон_ячеек_с_точками
SERVICEMAN_RANGE=Страница_и_диапазон_ячеек_c_инженерами
CHAT_ID=id_чата_для_пересылки_фото
```

Создать и активировать виртуально окружение:
```
python3.11 -m venv venv
. venv/bin/activate
```

Обновить пакетный менеджер и установить зависимости:
```
pip install -U pip
pip install -r backend/requirements.txt
pip install -r bot/requirements.txt
```

Запустить контейнеры с БД и ботом
```
cd infra
sudo docker compose up -d
```

Выполнить миграции БД, сбор статики и запустить backned:
```
cd ../backend
python manage.py migrate
python manage.py collectstatic
python manage.py runserver
```