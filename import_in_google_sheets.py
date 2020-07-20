import httplib2
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
import logging


# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# pip3 install --upgrade google-api-python-client
# pip3 install oauth2client


def main(data):
    CREDENTIALS_FILE = 'secret.json'  # имя файла с закрытым ключом

    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = discovery.build('sheets', 'v4', http=httpAuth)
    spreadsheet = service.spreadsheets().create(body={
        'properties': {'title': 'Parsing_Result', 'locale': 'ru_RU'},
        'sheets': [{'properties': {'sheetType': 'GRID',
                                   'sheetId': 0,
                                   'title': 'Сие есть название листа'}}]
    }).execute()
    logging.debug(f'spreadsheet = {spreadsheet}')
    logging.debug(f"https://docs.google.com/spreadsheets/d/{spreadsheet['spreadsheetId']}")

    driveService = discovery.build('drive', 'v3', http=httpAuth)
    shareRes = driveService.permissions().create(
        fileId=spreadsheet['spreadsheetId'],
        # body = {'type': 'anyone', 'role': 'reader'},  # доступ на чтение кому угодно
        body={'type': 'user', 'role': 'writer', 'emailAddress': 'my.tneu.fcit@gmail.com'},
        fields='id'
    ).execute()
    values = [['name', 'url', 'price_usd', 'price_uah', 'city', 'car_dealership']]
    for j in data:
        name = j['name']
        url = j['url']
        price_usd = j['price_usd']
        price_uah = j['price_uah']
        city = j['city']
        car_dealership = j['car_dealership']
        values.append([name, url, price_usd, price_uah, city, car_dealership])
    logging.debug(f'values = {values}')
    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet['spreadsheetId'], body={
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": f"A1:F{len(data)+1}",
             "majorDimension": "ROWS",
             "values": values},
        ]
    }).execute()
    return f"https://docs.google.com/spreadsheets/d/{spreadsheet['spreadsheetId']}"
