from django.contrib import admin

from .models import Post, Comment, Test, Question, Variant, UserAnswer, Attempt

admin.site.register(Post)
admin.site.register(Comment)

admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Variant)
admin.site.register(UserAnswer)
admin.site.register(Attempt)
