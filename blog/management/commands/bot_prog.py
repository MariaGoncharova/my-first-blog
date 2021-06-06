from datetime import datetime

from logging import getLogger
from django.core.management.base import BaseCommand
from django.conf import settings
from django.shortcuts import get_object_or_404
from telegram.utils.request import Request
from telegram import Bot, ParseMode, ReplyKeyboardRemove
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import Update
from telegram.ext import Updater, CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import CallbackQueryHandler

import blog
from blog.models import Profile, Test, StoreQuestion
from blog.utils import logger_factory

logger = getLogger(__name__)

debug_requests = logger_factory(logger=logger)

# `callback_data` -- это то, что будет присылать TG при нажатии на каждую кнопку.
# Поэтому каждый идентификатор должен быть уникальным
CALLBACK_BUTTON1 = "callback_button1"
CALLBACK_BUTTON2 = "callback_button2"
CALLBACK_BUTTON3 = "callback_button3"
CALLBACK_BUTTON4 = "callback_button4"
CALLBACK_BUTTON5 = "callback_button5"
CALLBACK_BUTTON_START_TEST = "callback_button_start_test"
CALLBACK_BUTTON_NEXT_QUESTION = "callback_button_next_question"
CALLBACK_BUTTON_HIDE_KEYBOARD = "callback_button9_hide"
CALLBACK_BUTTON_RESULT = "callback_button_result"
CALLBACK_BUTTON_TEST_LIST = "callback_button_test_list"

CALLBACK_BUTTON5_TIME = "callback_button5_time"

TITLES = {
    CALLBACK_BUTTON1: "1️⃣",
    CALLBACK_BUTTON2: "2️⃣",
    CALLBACK_BUTTON3: "️3️⃣",
    CALLBACK_BUTTON4: "️4️⃣",
    CALLBACK_BUTTON5: "5️⃣",
    CALLBACK_BUTTON_START_TEST: "Начать тестирование ✅",
    CALLBACK_BUTTON_NEXT_QUESTION: "Следующий вопрос ➡️",
    CALLBACK_BUTTON5_TIME: "Время ⏰",
    CALLBACK_BUTTON_HIDE_KEYBOARD: "Спрятать клавиатуру ⬇️",
    CALLBACK_BUTTON_RESULT: "Результат 📄",
    CALLBACK_BUTTON_TEST_LIST: "К списку тестов ⬅️",

}


def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Произошла ошибка: {e}'
            print(error_message)
            raise e

    return inner


# Список тестов
def get_test_inline_keyboard():
    """ Получить клавиатуру для списка тестов
        Эта клавиатура будет видна под каждым сообщением, где её прикрепили
    """
    # Каждый список внутри `keyboard` -- это один горизонтальный ряд кнопок
    keyboard = [
        # Каждый элемент внутри списка -- это один вертикальный столбец.
        # Сколько кнопок -- столько столбцов
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON1], callback_data=CALLBACK_BUTTON1),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON2], callback_data=CALLBACK_BUTTON2),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON3], callback_data=CALLBACK_BUTTON3),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON4], callback_data=CALLBACK_BUTTON4),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON5], callback_data=CALLBACK_BUTTON5),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_HIDE_KEYBOARD], callback_data=CALLBACK_BUTTON_HIDE_KEYBOARD),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# Уведомление о начале теста, кнопки назад и старт
def get_test_start_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_START_TEST], callback_data=CALLBACK_BUTTON_START_TEST),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_TEST_LIST], callback_data=CALLBACK_BUTTON_TEST_LIST),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_HIDE_KEYBOARD], callback_data=CALLBACK_BUTTON_HIDE_KEYBOARD),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# Уведомление о вариантах ответа
def get_variants_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON1], callback_data=CALLBACK_BUTTON1),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON2], callback_data=CALLBACK_BUTTON2),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON3], callback_data=CALLBACK_BUTTON3),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON4], callback_data=CALLBACK_BUTTON4),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_HIDE_KEYBOARD], callback_data=CALLBACK_BUTTON_HIDE_KEYBOARD),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# Уведомление о Следующем вопросе
def get_next_question_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_NEXT_QUESTION], callback_data=CALLBACK_BUTTON_NEXT_QUESTION),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_HIDE_KEYBOARD], callback_data=CALLBACK_BUTTON_HIDE_KEYBOARD),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# Уведомление о Последнем вопросе вопросе
def get_end_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_RESULT], callback_data=CALLBACK_BUTTON_RESULT),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_TEST_LIST], callback_data=CALLBACK_BUTTON_TEST_LIST),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_HIDE_KEYBOARD], callback_data=CALLBACK_BUTTON_HIDE_KEYBOARD),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


@log_errors
def keyboard_callback_handler(update: Update, context: CallbackContext):
    """ Обработчик ВСЕХ кнопок со ВСЕХ клавиатур
    """
    query = update.callback_query
    data = query.data
    now = datetime.now()
    tests_titles = [test.title for test in Test.objects.all()]
    titles = ' '.join(tests_titles)
    tests_id = [test.id for test in Test.objects.all()]
    # Обратите внимание: используется `effective_message`
    chat_id = update.effective_message.chat_id
    current_text = update.effective_message.text

    if data == CALLBACK_BUTTON1:
        query.edit_message_text(
            text=current_text,
            parse_mode=ParseMode.MARKDOWN,
        )
        tests_titles = [test.title for test in Test.objects.all().filter(id=tests_id[0])]
        titles_test = ''.join(tests_titles)
        # Отправим новое сообщение при нажатии на кнопку
        context.bot.send_message(
            chat_id=chat_id,
            text="Вы выбрали тест: " + titles_test,
            reply_markup=get_test_start_keyboard(),
        )

    elif data == CALLBACK_BUTTON_START_TEST:
        query.edit_message_text(
            text=current_text,
            parse_mode=ParseMode.MARKDOWN,
        )

        test = get_object_or_404(Test, pk=2)

        # questions = test.questions.filter(close_question=4)

        questions_set = test.questions.all()
        questions_lst = []

        # question = [question.close_question.description for question in questions_set]
        # question_title = ''.join(question)
        answers = [question.close_question.variants for question in questions_set]
        answer_lst = []
        # for answer in answers:
        #     for a in answer.all():
        #         answer_lst.append(a.description)

        for question in questions_set:
            questions_lst.append(question.close_question)

        question_answer_dict = dict(zip(questions_lst, [answer.all() for answer in answers]))
        print(question_answer_dict)

        for a, answer in question_answer_dict.items():
            print(a, answer_lst)
        for question, answer in question_answer_dict.items():
            print(question, answer_lst)

        # Отправим новое сообщение при нажатии на кнопку
        for question, answer in question_answer_dict.items():
            print(answer)
            update.message.reply_text(
                chat_id=chat_id,
                text="вопрос: \n" + question.description + '\n варианты ответа: \n' + '\n'.join(
                    [a.description for a in answer.all()]),
                reply_markup=get_next_question_keyboard()
            )
            # context.bot.send_message(
            #     chat_id=chat_id,
            #     text="вопрос: \n" + question.description + '\n варианты ответа: \n' + '\n'.join(
            #         [a.description for a in answer.all()]),
            #     reply_markup=get_next_question_keyboard()
            # )
        # print(questions_lst)



    # elif data == CALLBACK_BUTTON_NEXT_QUESTION:
    #     query.edit_message_text(
    #         text=current_text,
    #         parse_mode=ParseMode.MARKDOWN,
    #     )
    #
    #     test = get_object_or_404(Test, pk=2)
    #     questions = test.questions.filter(close_question=5)
    #     question = [question.close_question.description for question in questions]
    #     question_title = ''.join(question)
    #     answers = [question.close_question.variants for question in questions]
    #     answer_lst = []
    #
    #     for answer in answers:
    #         for a in answer.all():
    #             answer_lst.append(a.description)
    #
    #     answer = ' '.join(answer_lst)
    #     # Отправим новое сообщение при нажатии на кнопку
    #     context.bot.send_message(
    #         chat_id=chat_id,
    #         text="вопрос: \n" + question_title + ' варианты ответа: \n' + answer,
    #         reply_markup=get_next_question_keyboard()
    #     )

    elif data == CALLBACK_BUTTON_TEST_LIST:
        # Отправим новое сообщение при нажатии на кнопку
        context.bot.send_message(
            chat_id=chat_id,
            text="Доступные тесты: \n" + titles,
            reply_markup=get_test_inline_keyboard(),
        )

    elif data == CALLBACK_BUTTON_HIDE_KEYBOARD:
        # Спрятать клавиатуру
        # Работает только при отправке нового сообщение
        # Можно было бы отредактировать, но тогда нужно точно знать что у сообщения не было кнопок
        context.bot.send_message(
            chat_id=chat_id,
            text="Спрятали клавиатуру\n\nНажмите /start чтобы вернуть её обратно",
            reply_markup=ReplyKeyboardRemove(),
        )


# Начало диалога
@log_errors
def do_start(update: Update, context: CallbackContext):
    update.message.reply_text(
        text="Привет! Я бот для тестирования\nНажмите /help для вызова помощи."
             "\nНажмите /tests для вывода списка тестов.",
    )


# Начало теста
@log_errors
def do_tests(update: Update, context: CallbackContext):
    tests_titles = [test.title for test in Test.objects.all()]
    titles = ' '.join(tests_titles)
    update.message.reply_text(
        text="Доступные тесты: " + titles,
        reply_markup=get_test_inline_keyboard(),
    )


@log_errors
def do_help(update: Update, context: CallbackContext):
    update.message.reply_text(
        text="это учебный бот",
    )


@log_errors
def do_echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text

    # p, _ = Profile.objects.get_or_create(
    #     external_id=chat_id,
    #     defaults={
    #         'name': update.message.from_user.username,
    #     }
    # )

    reply_text = f'Ваш ID = {chat_id}\n{text}'
    update.message.reply_text(
        text=reply_text,
        reply_markup=get_test_inline_keyboard(),
    )


class Command(BaseCommand):
    # help = 'Telegram-bot'

    def handle(self, *args, **options):
        logger.info("Запускаем бота...")
        # 1 -- правильное подключение
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot = Bot(
            request=request,
            token=settings.TOKEN,
        )
        print(bot.get_me())

        # 2 -- обработчики
        updater = Updater(
            bot=bot,
            use_context=True,
        )

        start_handler = CommandHandler('start', do_start)
        help_handler = CommandHandler('help', do_help)
        test_handler = CommandHandler('tests', do_tests)
        message_handler = MessageHandler(Filters.text, do_echo)
        buttons_handler = CallbackQueryHandler(callback=keyboard_callback_handler)
        updater.dispatcher.add_handler(message_handler)
        updater.dispatcher.add_handler(start_handler)
        updater.dispatcher.add_handler(help_handler)
        updater.dispatcher.add_handler(test_handler)
        updater.dispatcher.add_handler(buttons_handler)

        # 3 -- запустить бесконечную обработку входящих сообщений
        updater.start_polling()
        # не прерывать скрипт до обработки всех сообщений
        updater.idle()
