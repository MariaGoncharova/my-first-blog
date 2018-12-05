from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, UserAdmin
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm

from .models import Post, Comment, Test, Question, Variant
from .models import User
from django.utils.translation import ugettext_lazy as _


admin.site.register(Post)
admin.site.register(Comment)

admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Variant)


admin.site.register(User, UserAdmin)



