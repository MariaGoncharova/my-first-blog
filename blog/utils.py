import functools

from blog.constants import TestType


def get_id_for_form_fields(test_type: TestType, number):
    id_name = '{test_type}_{number}'
    if test_type == TestType.CLOSE.value:
        id_name = id_name.format(test_type=TestType.CLOSE.value, number=number)
    if test_type == TestType.OPEN.value:
        id_name = id_name.format(test_type=TestType.OPEN.value, number=number)

    return id_name


def logger_factory(logger):
    """ Импорт функции происходит раньше чем загрузка конфига логирования.
        Поэтому нужно явно указать в какой логгер мы хотим записывать.
    """

    def debug_requests(f):

        @functools.wraps(f)
        def inner(*args, **kwargs):

            try:
                logger.debug('Обращение в функцию `{}`'.format(f.__name__))
                return f(*args, **kwargs)
            except Exception as e:
                logger.exception('Ошибка в функции `{}`'.format(f.__name__))
                # sentry_sdk.capture_exception(error=e)
                raise

        return inner

    return debug_requests
