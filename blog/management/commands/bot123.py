from datetime import datetime

from logging import getLogger
from django.core.management.base import BaseCommand
from django.conf import settings
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

from blog.models import Profile
from blog.utils import logger_factory

logger = getLogger(__name__)

debug_requests = logger_factory(logger=logger)

# `callback_data` -- это то, что будет присылать TG при нажатии на каждую кнопку.
# Поэтому каждый идентификатор должен быть уникальным
CALLBACK_BUTTON1_LEFT = "callback_button1_left"
CALLBACK_BUTTON2_RIGHT = "callback_button2_right"
CALLBACK_BUTTON3_MORE = "callback_button3_more"
CALLBACK_BUTTON4_BACK = "callback_button4_back"
CALLBACK_BUTTON5_TIME = "callback_button5_time"
CALLBACK_BUTTON6_PRICE = "callback_button6_price"
CALLBACK_BUTTON7_PRICE = "callback_button7_price"
CALLBACK_BUTTON8_PRICE = "callback_button8_price"
CALLBACK_BUTTON_HIDE_KEYBOARD = "callback_button9_hide"
CALLBACK_BUTTON1 = "callback_button1"
CALLBACK_BUTTON2 = "callback_button2"
CALLBACK_BUTTON3 = "callback_button3"
CALLBACK_BUTTON4 = "callback_button4"
CALLBACK_BUTTON5 = "callback_button5"
CALLBACK_BUTTON_NEXT_QUESTION = "callback_button_next_question"
CALLBACK_BUTTON_PREV_QUESTION = "callback_button_prev_question"
CALLBACK_BUTTON_START_TEST = "callback_button_start_test"

TITLES = {
    CALLBACK_BUTTON1_LEFT: "Новое сообщение ⚡️",
    CALLBACK_BUTTON2_RIGHT: "Отредактировать ✏️",
    CALLBACK_BUTTON3_MORE: "Ещё ➡️",
    CALLBACK_BUTTON4_BACK: "Назад ⬅️",
    CALLBACK_BUTTON5_TIME: "Время ⏰",
    CALLBACK_BUTTON6_PRICE: "BTC 💰",
    CALLBACK_BUTTON7_PRICE: "LTC 💰",
    CALLBACK_BUTTON8_PRICE: "ETH 💰",
    CALLBACK_BUTTON_HIDE_KEYBOARD: "Спрять клавиатуру",
    CALLBACK_BUTTON1: "1️⃣",
    CALLBACK_BUTTON2: "2️⃣",
    CALLBACK_BUTTON3: "️3️⃣",
    CALLBACK_BUTTON4: "️4️⃣",
    CALLBACK_BUTTON5: "5️⃣",
    CALLBACK_BUTTON_NEXT_QUESTION: "Следующий вопрос ➡️",
    CALLBACK_BUTTON_PREV_QUESTION: "Предыдущий вопрос ➡️",
    CALLBACK_BUTTON_START_TEST: "Начать тестирование ✅",
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
    ]
    return InlineKeyboardMarkup(keyboard)


# Кнопки вперед и назад после ответа на тест
def get_test_inline_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_NEXT_QUESTION], callback_data=CALLBACK_BUTTON_NEXT_QUESTION),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_PREV_QUESTION], callback_data=CALLBACK_BUTTON_PREV_QUESTION),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# Кнопки старт и назад после выбора теста
def get_test_start_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_START_TEST], callback_data=CALLBACK_BUTTON_START_TEST),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON4_BACK], callback_data=CALLBACK_BUTTON4_BACK),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_base_inline_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON1_LEFT], callback_data=CALLBACK_BUTTON1_LEFT),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON2_RIGHT], callback_data=CALLBACK_BUTTON2_RIGHT),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_HIDE_KEYBOARD], callback_data=CALLBACK_BUTTON_HIDE_KEYBOARD),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON3_MORE], callback_data=CALLBACK_BUTTON3_MORE),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_keyboard2():
    """ Получить вторую страницу клавиатуры для сообщений
        Возможно получить только при нажатии кнопки на первой клавиатуре
    """
    keyboard = [
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON5_TIME], callback_data=CALLBACK_BUTTON5_TIME),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON6_PRICE], callback_data=CALLBACK_BUTTON6_PRICE),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON7_PRICE], callback_data=CALLBACK_BUTTON7_PRICE),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON8_PRICE], callback_data=CALLBACK_BUTTON8_PRICE),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON4_BACK], callback_data=CALLBACK_BUTTON4_BACK),
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

    # Обратите внимание: используется `effective_message`
    chat_id = update.effective_message.chat_id
    current_text = update.effective_message.text

    if data == CALLBACK_BUTTON1_LEFT:
        # "Удалим" клавиатуру у прошлого сообщения
        # (на самом деле отредактируем его так, что текст останется тот же, а клавиатура пропадёт)
        query.edit_message_text(
            text=current_text,
            parse_mode=ParseMode.MARKDOWN,
        )
        # Отправим новое сообщение при нажатии на кнопку
        context.bot.send_message(
            chat_id=chat_id,
            text="Новое сообщение\n\ncallback_query.data={}".format(data),
            reply_markup=get_base_inline_keyboard(),
        )
    elif data == CALLBACK_BUTTON2_RIGHT:
        # Отредактируем текст сообщения, но оставим клавиатуру
        query.edit_message_text(
            text="Успешно отредактировано в {}".format(now),
            reply_markup=get_base_inline_keyboard(),
        )
    elif data == CALLBACK_BUTTON3_MORE:
        # Показать следующий экран клавиатуры
        # (оставить тот же текст, но указать другой массив кнопок)
        query.edit_message_text(
            text=current_text,
            reply_markup=get_keyboard2(),
        )
    elif data == CALLBACK_BUTTON4_BACK:
        # Показать предыдущий экран клавиатуры
        # (оставить тот же текст, но указать другой массив кнопок)
        query.edit_message_text(
            text=current_text,
            reply_markup=get_base_inline_keyboard(),
        )
    elif data == CALLBACK_BUTTON5_TIME:
        # Покажем новый текст и оставим ту же клавиатуру
        text = "*Точное время*\n\n{}".format(now)
        query.edit_message_text(
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_keyboard2(),
        )
    elif data in (CALLBACK_BUTTON6_PRICE, CALLBACK_BUTTON7_PRICE, CALLBACK_BUTTON8_PRICE):
        pair = {
            CALLBACK_BUTTON6_PRICE: "USD-BTC",
            CALLBACK_BUTTON7_PRICE: "USD-LTC",
            CALLBACK_BUTTON8_PRICE: "USD-ETH",
        }[data]

    elif data == CALLBACK_BUTTON_HIDE_KEYBOARD:
        # Спрятать клавиатуру
        # Работает только при отправке нового сообщение
        # Можно было бы отредактировать, но тогда нужно точно знать что у сообщения не было кнопок
        context.bot.send_message(
            chat_id=chat_id,
            text="Спрятали клавиатуру\n\nНажмите /start чтобы вернуть её обратно",
            reply_markup=ReplyKeyboardRemove(),
        )

    elif data == CALLBACK_BUTTON1:
        # Покажем новый текст и оставим ту же клавиатуру
        text = "*Вы выбрали тест*\n\n{}".format(now)
        # TODO: сделать вывод теста который выбрали
        context.bot.send_message(
            text=text,
            reply_markup=get_test_start_keyboard(),
        )

    elif data == CALLBACK_BUTTON_START_TEST:
        # "Удалим" клавиатуру у прошлого сообщения
        # (на самом деле отредактируем его так, что текст останется тот же, а клавиатура пропадёт)
        query.edit_message_text(
            text=current_text,
            parse_mode=ParseMode.MARKDOWN,
        )
        # Отправим новое сообщение при нажатии на кнопку
        context.bot.send_message(
            text="1 вопрос".format(data),
            reply_markup=get_base_inline_keyboard(),
        )


# Начало диалога
@log_errors
def do_start(update: Update, context: CallbackContext):
    update.message.reply_text(
        text="Привет! Я бот для тестирования\nНажмите /help для вызова помощи.\n",
        reply_markup=get_base_inline_keyboard(),
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
        message_handler = MessageHandler(Filters.text, do_echo)
        buttons_handler = CallbackQueryHandler(callback=keyboard_callback_handler)
        updater.dispatcher.add_handler(message_handler)
        updater.dispatcher.add_handler(start_handler)
        updater.dispatcher.add_handler(help_handler)
        updater.dispatcher.add_handler(buttons_handler)

        # 3 -- запустить бесконечную обработку входящих сообщений
        updater.start_polling()
        # не прерывать скрипт до обработки всех сообщений
        updater.idle()
