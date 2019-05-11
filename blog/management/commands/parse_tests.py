from django.core.management.base import BaseCommand
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from blog.models import Question, OpenQuestion, StoreQuestion

scope = ['https://www.googleapis.com/auth/spreadsheets']
document = '1nsLgrWgTi4gy1liZMlsFJf5orfrSXzZPX9iwdkui1XE'
open_questions_sheet = "Open_Questions"
closed_questions_sheet = "Closed_Questions"
token_file = 'diplomaproject-240220-d0d65406fe9d.json'


class Command(BaseCommand):

    @staticmethod
    def download_question(question_type, sheet):
        worksheet = sheet.worksheet(question_type)
        list_of_questions = worksheet.get_all_values()
        list_of_questions.pop(0)
        return list_of_questions

    @staticmethod
    def make_closed_questions(self, list_of_questions):
        closed_question = Question
        closed_questions_store = StoreQuestion
        for row in list_of_questions:
            closed_question.title = row[0]
            closed_question.description = row[1]
            closed_question.right_answer = row[3]
            for i in row[2]:
                print(i)

    @staticmethod
    def make_open_questions(list_of_questions):
        print(list_of_questions)

    def handle(self, *args, **options):
        # TODO: парсинг тестов
        credentials = ServiceAccountCredentials.from_json_keyfile_name(token_file, scope)
        google_client = gspread.authorize(credentials)
        google_table = google_client.open_by_key(document)
        parser = Command
        closed_questions = parser.downloadQuestions(closed_questions_sheet, google_table)
        open_questions = parser.downloadQuestions(open_questions_sheet, google_table)
        parser.makeOpenQuestions(open_questions)
        parser.makeClosedQuestions(closed_questions)


