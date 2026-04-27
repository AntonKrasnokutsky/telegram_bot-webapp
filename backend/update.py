import django
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coffee_bot_beckend.settings')
django.setup()

from django.contrib.auth import get_user_model

from points.models import ServiceMan


def transliterate(name: str) -> str:
   slovar = {
       'а': 'a',
       'б': 'b',
       'в': 'v',
       'г': 'g',
       'д': 'd',
       'е': 'e',
       'ё': 'yo',
       'ж': 'zh',
       'з': 'z',
       'и': 'i',
       'й': 'y',
       'к': 'k',
       'л': 'l',
       'м': 'm',
       'н': 'n',
       'о': 'o',
       'п': 'p',
       'р': 'r',
       'с': 's',
       'т': 't',
       'у': 'u',
       'ф': 'f',
       'х': 'h',
       'ц': 'c',
       'ч': 'ch',
       'ш': 'sh',
       'щ': 'sch',
       'ъ': '',
       'ы': 'y',
       'ь': '',
       'э': 'e',
       'ю': 'u',
       'я': 'ya',
       'А': 'A',
       'Б': 'B',
       'В': 'V',
       'Г': 'G',
       'Д': 'D',
       'Е': 'E',
       'Ё': 'YO',
       'Ж': 'ZH',
       'З': 'Z',
       'И': 'I',
       'Й': 'Y',
       'К': 'K',
       'Л': 'L',
       'М': 'M',
       'Н': 'N',
       'О': 'O',
       'П': 'P',
       'Р': 'R',
       'С': 'S',
       'Т': 'T',
       'У': 'U',
       'Ф': 'F',
       'Х': 'H',
       'Ц': 'C',
       'Ч': 'CH',
       'Ш': 'SH',
       'Щ': 'SCH',
       'Ъ': '',
       'Ы': 'y',
       'Ь': '',
       'Э': 'E',
       'Ю': 'U',
       'Я': 'YA',
       ',': '',
       '?': '',
       ' ': '_',
       '~': '',
       '!': '',
       '@': '',
       '#': '',
       '$': '',
       '%': '',
       '^': '',
       '&': '',
       '*': '',
       '(': '(',
       ')': ')',
       '-': '',
       '=': '',
       '+': '',
       ':': '',
       ';': '',
       '<': '',
       '>': '',
       '\'': '',
       '"': '',
       '\\': '',
       '/': '',
       '№': '',
       '[': '',
       ']': '',
       '{': '',
       '}': '',
       'ґ': '',
       'ї': '',
       'є': '',
       'Ґ': 'g',
       'Ї': 'i',
       'Є': 'e',
       '—': '',
    }

   for key in slovar:
      name = name.replace(key, slovar[key])
   return name


def password_generator(count: int = 6) -> str:
    from random import randint
    chars_password = '0123456789'
    password = ''
    for c in range(count):
        password += chars_password[randint(0, len(chars_password) - 1)]

    return password


def create_service_man_user():
    User = get_user_model()
    logpass = []
    with open('logpass.txt', 'w', encoding='utf-8') as f:
        for service_man in ServiceMan.objects.filter(
            activ=True,
            office_engineer=True
        ):
            login = transliterate(service_man.name)
            password = password_generator()
            try:
                user = User.objects.create_user(
                    username=login,
                    password=password,
                    is_staff=True,
                )
                user.userprofile.telegram_id = service_man.telegram_id
                user.userprofile.office_engineer = service_man.office_engineer
                user.userprofile.save()
                record = (
                    f'Имя: {service_man.name}, '
                    'login: {login}, pass: {password}\n'
                )
                f.write(record)
                logpass.append(record)
            except:
                pass
    print(*logpass)


def update():
    # recalculate_filments_and_machine_in_order()
    create_service_man_user()


if __name__ == '__main__':
    update()
