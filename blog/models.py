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
    class Meta:
        verbose_name = 'Новости'
        verbose_name_plural = 'Новости'

    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        verbose_name='Текст новости'
    )
    news_description = models.TextField(
        default='',
        verbose_name='Превью новости'
    )

    created_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата создания'
    )
    published_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Дата публикации'
    )

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title


class Comment(models.Model):
    class Meta:
        verbose_name = 'Комментарии'
        verbose_name_plural = 'Комментарии'

    post = models.ForeignKey(
        'blog.Post',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.CharField(
        max_length=200,
        verbose_name='Автор'
    )
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    created_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата создания'
    )
    approved_comment = models.BooleanField(
        default=False,
        verbose_name='Подтверженние комментария'
    )

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return self.text


class Variant(models.Model):
    class Meta:
        verbose_name = 'Варианты ответа'
        verbose_name_plural = 'Варианты ответа'

    description = models.TextField(
        verbose_name='Вариант ответа'
    )

    def __str__(self):
        return self.description


class Question(models.Model):
    class Meta:
        verbose_name = 'Закрытые вопросы'
        verbose_name_plural = 'Закрытые вопросы'

    title = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Вопрос'
    )
    right_answer = models.ForeignKey(
        Variant,
        related_name='right',
        on_delete=models.CASCADE,
        verbose_name='Правильный ответ'
    )

    variants = models.ManyToManyField(
        Variant,
        verbose_name='Варианты ответа'
    )

    def create_form(self, i):
        from blog.forms import TestForm

        label = self.description
        variants = self.variants.order_by('pk').all()
        return TestForm(label=label, variants=variants, i=i)

    def is_right(self, answer):
        return self.right_answer == answer

    def __str__(self):
        return self.title


class OpenQuestion(models.Model):
    class Meta:
        verbose_name = 'Открытые вопросы'
        verbose_name_plural = 'Открытые вопросы'

    title = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Вопрос'
    )

    def create_form(self, i):
        from blog.forms import TestForm

        label = self.description
        return TestForm(label=label, test_type=TestType.OPEN, i=i)

    def __str__(self):
        return self.title


class StoreQuestion(models.Model):
    class Meta:
        verbose_name = 'Хранилище вопросов'
        verbose_name_plural = 'Хранилище вопросов'
    test_type = models.CharField(
        max_length=128,
        choices=TEST_TYPE,
        default=TestType.CLOSE.value,
        verbose_name='Тип теста'
    )
    close_question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Закрытый вопрос'
    )
    open_question = models.ForeignKey(
        OpenQuestion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Открытый вопрос'
    )

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
        return f'Тип: {self.test_type} -> закрытый: {self.close_question}, Открытый: {self.open_question}'


class Test(models.Model):
    class Meta:
        verbose_name = 'Тесты'
        verbose_name_plural = 'Тесты'

    title = models.CharField(
        max_length=128,
        verbose_name='Заголовок'
    )
    date_create = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата создания'
    )

    questions = models.ManyToManyField(
        StoreQuestion,
        verbose_name='Вопросы'
    )

    def __str__(self):
        return self.title


class StoreAnswer(models.Model):
    class Meta:
        verbose_name = 'Хранилище ответов'
        verbose_name_plural = 'Хранилище ответов'

    test_type = models.CharField(
        max_length=128,
        choices=TEST_TYPE,
        default=TestType.CLOSE.value,
        verbose_name='Тип теста'
    )

    close_answer = models.ForeignKey(
        Variant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Закрытый ответ'
    )
    open_answer = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        verbose_name='Открытый ответ'
    )

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
        return f'Тип вопроса: {self.test_type} Ответ: {answer}'


class UserAnswer(models.Model):
    class Meta:
        verbose_name = 'Ответы пользователей'
        verbose_name_plural = 'Ответы пользователей'

    question = models.ForeignKey(
        StoreQuestion,
        on_delete=models.CASCADE,
        verbose_name='Вопрос'
    )
    answer = models.ForeignKey(
        StoreAnswer,
        on_delete=models.CASCADE,
        verbose_name='Ответ'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    status = models.CharField(
        max_length=128,
        choices=ATTEMPT_STATUS,
        default=AttemptStatus.PENDING.value,
        verbose_name='Статус'
    )

    def __str__(self):
        return f' Пользователь: {self.user} Статус: {self.status}'


class Attempt(models.Model):
    class Meta:
        verbose_name = 'Попытки'
        verbose_name_plural = 'Попытки'

    passage_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата прохождения'
    )
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        verbose_name='Тест'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    user_answer = models.ManyToManyField(
        UserAnswer,
        verbose_name='Ответ пользователя'
    )

    status = models.CharField(
        max_length=128,
        choices=ATTEMPT_STATUS,
        default=AttemptStatus.PENDING.value,
        verbose_name='Статус'
    )

    def __str__(self):
        user_answer = list(map(lambda item: str(item), self.user_answer.values()))
        return f'Тест: {self.test}, Пользователь: {self.user} Статус: {self.status}'

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


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    instructor = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Инструктор'
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата рождения'
    )
    phone_number = models.CharField(
        max_length=17,
        null=True,
        blank=True,
        verbose_name='Номер телефона'
    )
    medical_certificate = models.BooleanField(
        default=False,
        blank=True,
        verbose_name='Медицинская справка'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='аватар',
    )

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профиль пользователя'

    def __str__(self):
        return f'Пользователь: {self.user}, Инструктор: {self.instructor}'