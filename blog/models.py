from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.utils import timezone

from blog.constants import TestType, AttemptStatus

TEST_TYPE = (
    (TestType.CLOSE.value, TestType.CLOSE.value),
    (TestType.OPEN.value, TestType.OPEN.value),
)
ATTEMPT_STATUS = (
    (AttemptStatus.PASSED.value, AttemptStatus.PASSED.value),
    (AttemptStatus.NOT_PASSED.value, AttemptStatus.NOT_PASSED.value),
    (AttemptStatus.PENDING.value, AttemptStatus.PENDING.value),
)


class Post(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    news_description = models.TextField(default='')

    created_date = models.DateTimeField(
        default=timezone.now)
    published_date = models.DateTimeField(
        blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return self.text


class Variant(models.Model):
    description = models.TextField()

    def __str__(self):
        return self.description


# Закртый вопрос
class Question(models.Model):
    title = models.CharField(max_length=128, null=True, blank=True)
    description = models.TextField()
    right_answer = models.ForeignKey(Variant, related_name='right', on_delete=models.CASCADE)

    variants = models.ManyToManyField(Variant)

    def create_form(self, i):
        from blog.forms import TestForm

        label = self.description
        variants = self.variants.order_by('pk').all()
        return TestForm(label=label, variants=variants, i=i)

    def is_right(self, answer):
        return self.right_answer == answer

    def __str__(self):
        return self.title


# Открытый вопрос
class OpenQuestion(models.Model):
    title = models.CharField(max_length=128, null=True, blank=True)
    description = models.TextField()

    def create_form(self, i):
        from blog.forms import TestForm

        label = self.description
        return TestForm(label=label, test_type=TestType.OPEN, i=i)

    def __str__(self):
        return self.title


class StoreQuestion(models.Model):
    # открытый или закрытый вопрос
    test_type = models.CharField(max_length=128, choices=TEST_TYPE, default=TestType.CLOSE.value)

    close_question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    open_question = models.ForeignKey(OpenQuestion, on_delete=models.CASCADE, null=True, blank=True)

    def create_question(self):
        if self.test_type == TestType.CLOSE.value:
            question_form = self.close_question.create_form(self.pk)
        elif self.test_type == TestType.OPEN.value:
            question_form = self.open_question.create_form(self.pk)

        return question_form

    def get_question(self):
        question = None
        if self.test_type == TestType.CLOSE.value:
            question = self.close_question
        elif self.test_type == TestType.OPEN.value:
            question = self.open_question

        return self.test_type, question

    def __str__(self):
        return f'Type: {self.test_type} -> close: {self.close_question}, open: {self.open_question}'


class Test(models.Model):
    title = models.CharField(max_length=128)
    date_create = models.DateTimeField(default=timezone.now)

    questions = models.ManyToManyField(StoreQuestion)

    def __str__(self):
        return self.title


class StoreAnswer(models.Model):
    test_type = models.CharField(max_length=128, choices=TEST_TYPE, default=TestType.CLOSE.value)

    close_answer = models.ForeignKey(Variant, on_delete=models.CASCADE, null=True, blank=True)
    open_answer = models.CharField(max_length=512, null=True, blank=True)

    @staticmethod
    def create_answer(test_type: TestType, data):
        store_answer = StoreAnswer()
        store_answer.test_type = test_type

        if test_type == TestType.CLOSE.value:
            store_answer.close_answer = data
        elif test_type == TestType.OPEN.value:
            store_answer.open_answer = data

        store_answer.save()

        return store_answer

    def get_answer(self):
        answer = None
        if self.test_type == TestType.CLOSE.value:
            answer = self.close_answer
        elif self.test_type == TestType.OPEN.value:
            answer = self.open_answer

        return self.test_type, answer

    def __str__(self):
        if self.test_type == TestType.CLOSE.value:
            answer = self.close_answer
        elif self.test_type == TestType.OPEN.value:
            answer = self.open_answer
        return f'Type: {self.test_type} Answer: {answer}'


class UserAnswer(models.Model):
    question = models.ForeignKey(StoreQuestion, on_delete=models.CASCADE)
    answer = models.ForeignKey(StoreAnswer, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=128, choices=ATTEMPT_STATUS, default=AttemptStatus.PENDING.value)

    def __str__(self):
        return f'Question: {self.question}, User: {self.user} Answer: {self.answer} Status: {self.status}'


class Attempt(models.Model):
    passage_date = models.DateTimeField(default=timezone.now)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_answer = models.ManyToManyField(UserAnswer)

    status = models.CharField(max_length=128, choices=ATTEMPT_STATUS, default=AttemptStatus.PENDING.value)

    def __str__(self):
        user_answer = list(map(lambda item: str(item), self.user_answer.values()))
        return f'Test: {self.test}, User: {self.user}, Answer: {user_answer} Status: {self.status}'

    def resolve_attempt(self):
        user_answers = self.user_answer.all()
        right_answer = user_answers.filter(status=AttemptStatus.PASSED.value)
        pending = user_answers.filter(status=AttemptStatus.PENDING.value)

        if len(right_answer) == len(user_answers):
            self.status = AttemptStatus.PASSED
            self.save()
        elif len(pending) == 0:
            self.status = AttemptStatus.NOT_PASSED
            self.save()
