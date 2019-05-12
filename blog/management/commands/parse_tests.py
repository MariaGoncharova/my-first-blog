from django.core.management.base import BaseCommand
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from blog.models import Question, OpenQuestion, Variant, StoreAnswer
from django.db import models

scope = ['https://www.googleapis.com/auth/spreadsheets']
document = '1nsLgrWgTi4gy1liZMlsFJf5orfrSXzZPX9iwdkui1XE'
open_questions_sheet = "Open_Questions"
closed_questions_sheet = "Closed_Questions"
token_file = 'diplomaproject-240220-d0d65406fe9d.json'


class Command(BaseCommand):

    @staticmethod
    def download_questions(questions_sheet, sheet):
        worksheet = sheet.worksheet(questions_sheet)
        list_of_questions = worksheet.get_all_values()
        list_of_questions.pop(0)
        return list_of_questions

    @staticmethod
    def make_closed_questions(list_of_questions):
        for row in list_of_questions:
            exist = Question.objects.filter(title=row[0]).exists()
            if exist:
                right_answer = Variant(description=row[3])
                right_answer.save()
                answers_str = row[2]
                answer = ""
                question = Question(title=row[0], description=row[1], right_answer=right_answer)
                question.save()
                for ch in answers_str:
                    if not ch == ';':
                        answer = answer + ch
                    else:
                        variant = Variant(description=answer)
                        variant.save()
                        variant_exist = question.variants.filter(description=answer).exists()
                        print(variant_exist)
                        if not variant_exist:
                            question.variants.add(variant)
                        print(variant)
                        answer = ""

    @staticmethod
    def make_open_questions(list_of_questions):
        question = OpenQuestion
        for row in list_of_questions:
            exist = question.objects.filter(title=row[0]).exists()
            if not exist:
                question.objects.create(title=row[0], description=row[1])

    def handle(self, *args, **options):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(token_file, scope)
        google_client = gspread.authorize(credentials)
        google_table = google_client.open_by_key(document)
        closed_questions = self.download_questions(closed_questions_sheet, google_table)
        open_questions = self.download_questions(open_questions_sheet, google_table)
        self.make_open_questions(open_questions)
        self.make_closed_questions(closed_questions)
