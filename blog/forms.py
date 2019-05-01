from django import forms
from django.forms import Textarea

from blog.constants import TestType
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': Textarea(attrs={
                'class': 'form-control',
                'cols': 80, 'rows': 3,
            }),
        }


FAVORITE_COLORS_CHOICES = (
    (1, 1),
    (2, 2),
    (3, 3),
)


def get_choices(variants):
    ch = tuple([(variant.description, variant.description) for i, variant in enumerate(variants)])
    return ch


class TestForm(forms.Form):

    def __init__(self, label, i, test_type=TestType.CLOSE, variants=None, *args, **kwarg):
        super(TestForm, self).__init__(*args, **kwarg)
        if test_type == TestType.CLOSE:
            self.fields[f'variants_{i}'] = forms.MultipleChoiceField(
                label=label,
                required=True,
                widget=forms.RadioSelect,
                choices=get_choices(variants),
            )
        else:
            self.fields[f'variants_{i}'] = forms.CharField(widget=forms.Textarea)


