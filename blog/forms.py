from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


FAVORITE_COLORS_CHOICES = (
    (1, 1),
    (2, 2),
    (3, 3),
)


class TestForm(forms.Form):
    variants = forms.MultipleChoiceField(
        required=False,
        widget=forms.RadioSelect,
        choices=FAVORITE_COLORS_CHOICES,
    )
