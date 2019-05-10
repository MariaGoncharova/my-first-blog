from django.core.management.base import BaseCommand
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://www.googleapis.com/auth/spreadsheets']

credentials = ServiceAccountCredentials.from_json_keyfile_name('diplomaproject-240220-d0d65406fe9d.json', scope)

gc = gspread.authorize(credentials)

wks = gc.open_by_key('1nsLgrWgTi4gy1liZMlsFJf5orfrSXzZPX9iwdkui1XE')
worksheet = wks.worksheet("Closed_Questions")

val = worksheet.acell('B2').value

print(val)

class Command(BaseCommand):

    def handle(self, *args, **options):
        # TODO: парсинг тестов
        print('hello')
