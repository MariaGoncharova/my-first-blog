from typing import List

from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView

from blog.constants import TestType, AttemptStatus
from blog.utils import get_id_for_form_fields
from blog.models import Post, Test, Attempt, Variant, StoreQuestion, StoreAnswer, UserAnswer
from blog.forms import PostForm, CommentForm, CheckOpenQuestionForm


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    return render(request, 'blog/news_list.html', {'posts': posts})


def post_detail(request, pk):
    form = CommentForm()
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/news_page.html', {
        'post': post,
        'form': form
    })

@login_required
def post_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})


@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)


@login_required
def publish(self):
    self.published_date = timezone.now()
    self.save()


@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('post_list')


@login_required
def create_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/news_page.html', {'form': form})


@login_required
def tests_list(request):
    tests = Test.objects.all()
    return render(request, 'tests/tests.html', {'tests': tests})


@login_required
def get_my_tests(request):
    attempts = Attempt.objects.filter(user=request.user)
    return render(request, 'blog/profile.html', {'attempts': attempts})


@login_required
def get_user_list(request):
    attempts = Attempt.objects.order_by('passage_date').all()
    users = {attempt.user for attempt in attempts}
    return render(request, 'check_pannel/user_list.html', {'users': users})


@login_required
def resolve_test(request, attempt):
    attempt = Attempt.objects.filter(pk=attempt).first()
    user_answers: List[UserAnswer] = attempt.user_answer.filter(question__test_type=TestType.OPEN.value)
    if request.method == 'POST':
        for user_answer in user_answers:
            description = request.POST.get(str(user_answer.pk))
            user_answer.status = description
            user_answer.save()

        attempt.resolve_attempt()
        return redirect('user-tests', user=attempt.user.pk)
    else:
        forms = []
        for user_answer in user_answers:
            question_type, question = user_answer.question.get_question()
            _, answer = user_answer.answer.get_answer()
            label = (
                f'question -> {question};;;\n'
                f'answer -> {answer}\n'
            )
            forms.append(CheckOpenQuestionForm(label=label, i=user_answer.pk))

        return render(request, 'check_pannel/resolve_test.html', {'forms': forms})


@login_required
def get_user_tests(request, user):
    user = User.objects.filter(pk=user).first()
    attempts = Attempt.objects.filter(user=user)
    return render(request, 'check_pannel/user_tests.html', {'attempts': attempts, 'user': user})


@login_required
def render_test(request, pk):
    test = get_object_or_404(Test, pk=pk)
    if request.method == 'POST':
        user = request.user

        questions: StoreQuestion = test.questions.order_by('pk').all()

        attempt = Attempt.objects.create(test=test, user=user)

        for store_question in questions:
            description = request.POST.get(get_id_for_form_fields(store_question.test_type, store_question.pk))

            status = AttemptStatus.PENDING.value
            if store_question.test_type == TestType.CLOSE.value:
                variant = Variant.objects.filter(description=description).first()
                store_answer = StoreAnswer.create_answer(store_question.test_type, variant)
                status = (
                    AttemptStatus.PASSED.value
                    if store_question.close_question.is_right(variant)
                    else AttemptStatus.NOT_PASSED.value
                )
            elif store_question.test_type == TestType.OPEN.value:
                store_answer = StoreAnswer.create_answer(store_question.test_type, description)

            attempt.user_answer.create(question=store_question, answer=store_answer, user=user, status=status)

        attempt.save()
        attempt.resolve_attempt()

        return redirect('my_tests')

    else:
        forms = []
        for store_question in test.questions.order_by('pk').all():
            forms.append(store_question.create_question())
    return render(request, 'tests/test.html', {'test': test, 'forms': forms})


class TestView(TemplateView):
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
