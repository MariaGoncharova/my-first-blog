from django.apps import AppConfig


class TestSystem(AppConfig):
    name = 'blog'
    verbose_name = 'Система тестирования'


default_app_config = "blog.TestSystem"