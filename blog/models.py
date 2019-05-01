from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


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


class Question(models.Model):
    title = models.CharField(max_length=128, null=True, blank=True)
    description = models.TextField()
    right_answer = models.ForeignKey(Variant, related_name='right', on_delete=models.CASCADE)

    variants = models.ManyToManyField(Variant)

    def is_right(self, answer):
        return self.right_answer.description == answer

    def __str__(self):
        return self.title


class Test(models.Model):
    title = models.CharField(max_length=128)
    date_create = models.DateTimeField(default=timezone.now)

    questions = models.ManyToManyField(Question)

    def __str__(self):
        return self.title
