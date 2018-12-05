from django.contrib import admin

from .models import Post, Comment, Test, Question, Variant


admin.site.register(Post)
admin.site.register(Comment)

admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Variant)



