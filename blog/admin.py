from django.contrib import admin
from .forms import ProfileForm
from .models import Post, Comment, Test, Question, Variant, UserAnswer, Attempt, StoreQuestion, OpenQuestion, \
    StoreAnswer, Profile

admin.site.register(Post)
admin.site.register(Comment)

admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Variant)
admin.site.register(UserAnswer)
admin.site.register(Attempt)
admin.site.register(StoreQuestion)
admin.site.register(OpenQuestion)
admin.site.register(StoreAnswer)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'name')
    form = ProfileForm

#
# @admin.register(Message)
# class MessageAdmin(admin.ModelAdmin):
#     list_display = ('id', 'profile', 'text', 'created_at')

