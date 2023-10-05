import httplib2
import os

from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

load_dotenv()

CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')


def get_service_sacc():
    creds_json = os.path.dirname(__file__) + '/' + CREDENTIALS_FILE
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    creds_service = ServiceAccountCredentials.from_json_keyfile_name(
        creds_json,
        scopes
    ).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)


if __name__ == '__main__':
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    SHEET_ID = os.getenv('SHEET_ID')
    resp = get_service_sacc().spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='Лист1'
    ).execute()
    print(resp)
    body = {
        'values':
        [[
            '12.09.2023 23:51:48',
            'expert@googlesheets.pro',
            'Канат Адилбеков',
            'РдСП--Ростов Герасименко 17 к 4 Магнит /:Скреперист:/ =тд004= 27.09.22 (:СО-АВ:)',
            '₽1\xa0500',
            '0',
            '1',
            '1',
            '1',
            '200',
            '2',
            '100',
            '100',
            '250',
            '50',
            '',
            '',
            '',
            '',
            '',
            'https://www.appsheet.com/template/gettablefileurl?appName=%D0%A3%D1%87%D0%B5%D1%82-208520581&tableName=%D0%9E%D0%B1%D1%81%D0%BB%D1%83%D0%B6%D0%B8%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5&fileName=%D0%9E%D0%B1%D1%81%D0%BB%D1%83%D0%B6%D0%B8%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5_Images%2F8.%D0%A4%D0%BE%D1%82%D0%BE1.164024.png'
        ]]}
    resp = get_service_sacc().spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='Лист1',
        # valueInputOption="RAW",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
