from django.core.management.base import BaseCommand
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from blog.constants import TestType
from blog.models import Question, OpenQuestion, Variant, StoreQuestion

SCOPE = ['https://www.googleapis.com/auth/spreadsheets']
DOCUMENT_ID = '1nsLgrWgTi4gy1liZMlsFJf5orfrSXzZPX9iwdkui1XE'
OPEN_QUESTIONS_SHEET = "Open_Questions"
CLOSED_QUESTIONS_SHEET = "Closed_Questions"
TOKEN_FILE = 'diplomaproject-240220-d0d65406fe9d.json'


class Command(BaseCommand):

    @staticmethod
    def download_questions(questions_sheet, table):
        worksheet = table.worksheet(questions_sheet)
        list_of_questions = worksheet.get_all_values()
        # удаляем строку с названием столбцов
        list_of_questions.pop(0)
        return list_of_questions

    @staticmethod
    def make_closed_questions(list_of_questions):
        for row in list_of_questions:
            question_exist = Question.objects.filter(title=row[0]).exists()
            if not question_exist:

                right_answer = Variant.objects.filter(description=row[3]).first()
                if not right_answer:
                    right_answer = Variant.objects.create(description=row[3])

                answers_str: str = row[2]
                question = Question.objects.create(title=row[0], description=row[1], right_answer=right_answer)

                for answer in answers_str.split(';'):
                    # Тут точно не работает
                    # надо проверить нахождение ответа в manytomanyfield
                    variant = Variant.objects.filter(description=answer).first()
                    if not variant:
                        variant = Variant.objects.create(description=answer)

                    question.variants.add(variant)

                question.save()

                StoreQuestion.objects.create(test_type=TestType.CLOSE.value, close_question=question)

    @staticmethod
    def make_open_questions(list_of_questions):
        for row in list_of_questions:
            question_exist = OpenQuestion.objects.filter(title=row[0]).exists()
            if not question_exist:
                question = OpenQuestion.objects.create(title=row[0], description=row[1])
                StoreQuestion.objects.create(test_type=TestType.OPEN.value, open_question=question)

    def handle(self, *args, **options):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(TOKEN_FILE, SCOPE)
        google_client = gspread.authorize(credentials)
        google_table = google_client.open_by_key(DOCUMENT_ID)
        closed_questions = self.download_questions(CLOSED_QUESTIONS_SHEET, google_table)
        open_questions = self.download_questions(OPEN_QUESTIONS_SHEET, google_table)
        self.make_open_questions(open_questions)
        self.make_closed_questions(closed_questions)