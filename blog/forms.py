from django import forms
from django.forms import Textarea

from blog.constants import TestType, AttemptStatus
from blog.utils import get_id_for_form_fields
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
            self.fields[get_id_for_form_fields(TestType.CLOSE, i)] = forms.MultipleChoiceField(
                label=label,
                required=True,
                widget=forms.RadioSelect,
                choices=get_choices(variants),
            )
        elif test_type == TestType.OPEN:
            self.fields[get_id_for_form_fields(TestType.OPEN, i)] = forms.CharField(widget=forms.Textarea, label=label)


class CheckOpenQuestionForm(forms.Form):

    def __init__(self, label, i, *args, **kwarg):
        super(CheckOpenQuestionForm, self).__init__(*args, **kwarg)
        self.fields[i] = forms.MultipleChoiceField(
            label=label,
            required=True,
            widget=forms.RadioSelect,
            choices=(
                (AttemptStatus.PASSED.value, AttemptStatus.PASSED.value),
                (AttemptStatus.NOT_PASSED.value, AttemptStatus.NOT_PASSED.value),
            ),
        )
