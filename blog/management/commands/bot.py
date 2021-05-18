from django.core.management.base import BaseCommand
from django.conf import settings
from telegram.utils.request import Request
from telegram import Bot
from telegram import Update
from telegram.ext import Updater, CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters

from blog.models import Profile


def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Произошла ошибка: {e}'
            print(error_message)
            raise e

    return inner


# Начало диалога
@log_errors
def do_start(bot: Bot, update: Update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text='Привет! Отправь мне что-нибудь',
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
    )


class Command(BaseCommand):
    # help = 'Telegram-bot'

    def handle(self, *args, **options):
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
        updater.dispatcher.add_handler(message_handler)
        updater.dispatcher.add_handler(start_handler)
        updater.dispatcher.add_handler(help_handler)

        # 3 -- запустить бесконечную обработку входящих сообщений
        updater.start_polling()
        # не прерывать скрипт до обработки всех сообщений
        updater.idle()
