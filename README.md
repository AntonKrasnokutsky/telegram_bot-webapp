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
- Django tables2 2.7.0


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
URL_AUDIT=https://{domain}/audit/
CREDENTIALS_FILE=json_доступа_сервисного аккаунта
SPREADSHEET_ID=ID_таблицы_google
SHEET_REPEAR=страница_сохранения_данных_ремонта
URL_API_POINTS=https://{domain}/api/points/
CHAT_ID=id_чата_для_пересылки_фото
API_USER=пользоватль
API_PASSWORD=пароль
DB_ENGINE=django.db.backends.postgresql
DB_HOST=адрес БД, например localhost
DB_PORT=порт БД
DOMAIN_NAME=доменное имя
POSTGRES_DB=название базы
POSTGRES_PASSWORD=пароль базы
POSTGRES_USER=пользователь базы
SECRET_KEY=секретный ключ Django
URL_API_AUTH=https://{domain}/api/auth/token/login/
URL_API_POINTS=https://{domain}/api/points/
URL_API_SERVICE=https://{domain}/api/v2/services/
URL_API_REPAIR=https://{domain}/api/v2/repairs/
URL_API_AUDIT=https://{domain}/api/v2/audit/
URL_API_SERVICE_MAN= https://{domain}/api/v2/serviceman/
```

Запустить контейнеры
```
cd infra
sudo docker compose up -d
```

Выполнить миграции БД, сбор статики и запустить backned:
```
docker compose exec -it backend python /app/manage.py migrate
```

Собрать статику
```
docker compose exec -it backend python /app/manage.py collectstatic
```

API

Получение токена
POST: `https://<domainname>/api/auth/token/login/`
```
{
    "password": "password",
    "username": "username"
}
```

Ответ:
```
{
    "auth_token": "token"
}
```

Только для авторизованных запросов
Получение списка проведенных обслуживаний
GET: `https://<domainname>/api/v2/services/`
Дополнительные параметры в запросе (не обязательно):
```
{
    "frome_date": "13.10.2023", # ответ должен содержать записи с даты (включительно)
    "before_date": "01.11.2023" # ответ должен содержать записи по даты (включительно)
}
```
или GET: `https://<domainname>/api/v2/services/?date_after=<гггг-мм-дд>&date_before=<гггг-мм-дд>`

при наличии только одного параметра в ответе будут содержаться данные от или до даты указанной в запросе

Получение списка проведенных ремонтов
GET: `https://<domainname>/api/repairs/`
Дополнительные параметры в запросе (не обязательно):
```
{
    "frome_date": "13.10.2023", # ответ должен содержать записи с даты (включительно)
    "before_date": "01.11.2023" # ответ должен содержать записи по даты (включительно)
}
```
при наличии только одного параметра в ответе будут содержаться данные от или до даты указанной в запросе


Эндпоинт работы с сотрудникам(доступно только зарегистрированным инженерам)
`https://<domainname>/api/v2/serviceman/`
get запрос возвращает список сотрудников
POST регистрирует сотрдника
```
{
    "name": "Имя",
    "telegram_id": <ID нового сотрудника в telegram>
}
```
Post с указанием Id записи в БД инвертирует статус сотрудника работает/уволен

Обновление списка точек обслуживания
GET: `https://<domainname>/api/points/`