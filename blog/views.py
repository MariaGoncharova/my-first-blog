from functools import reduce

from django.utils import timezone

from blog.constants import TestType
from blog.utils import get_id_for_form_fields
from .models import Post, Test, Attempt, Variant, StoreQuestion, StoreAnswer
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm, CommentForm, TestForm
from django.contrib.auth.decorators import login_required


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
def tests(request):
    tests = Test.objects.all()
    return render(request, 'tests/tests.html', {'tests': tests})


@login_required
def test(request, pk):
    test = get_object_or_404(Test, pk=pk)
    if request.method == 'POST':
        user = request.user

        questions: StoreQuestion = test.questions.order_by('pk').all()

        attempt = Attempt.objects.create(test=test, user=user)

        for store_question in questions:
            description = request.POST.get(get_id_for_form_fields(store_question.test_type, store_question.pk))

            if store_question.test_type == TestType.CLOSE.value:
                variant = Variant.objects.filter(description=description).first()
                store_answer = StoreAnswer.create_answer(store_question.test_type, variant)
            elif store_question.test_type == TestType.OPEN.value:
                store_answer = StoreAnswer.create_answer(store_question.test_type, description)

            attempt.user_answer.create(question=store_question, answer=store_answer, user=user)

        attempt.save()

        return render(
            request,
            'tests/result.html',
            {'rights': 1, 'total': 1, 'procent': 1}
        )

    else:
        forms = []
        for store_question in test.questions.order_by('pk').all():
            forms.append(store_question.create_question())
    return render(request, 'tests/test.html', {'test': test, 'forms': forms})


@login_required
def post_new(request):
    if request.method == "POST":
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
