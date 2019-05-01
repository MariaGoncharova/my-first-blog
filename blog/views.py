from functools import reduce

from django.utils import timezone
from .models import Post, Test
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
    if request.method == "POST":
        count_of_answer = 0
        for post_keys in request.POST.keys():
            if 'variants' in post_keys:
                count_of_answer += 1
        questions = test.questions.order_by('pk').all()
        answers = []
        for i, question in enumerate(questions):
            answers.append(question.is_right(request.POST.get('variants_{i}'.format(i=i))))
        rights = 0
        for item in answers:
            if item:
                rights += 1

        return render(request, 'tests/result.html',
                      {'rights': rights, 'total': len(answers), 'procent': int(rights / len(answers) * 100)})

    else:
        forms = []
        for i, question in enumerate(test.questions.order_by('pk').all()):
            label = question.description
            var = question.variants.order_by('pk').all()
            forms.append(TestForm(label=label, variants=var, i=i))
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
