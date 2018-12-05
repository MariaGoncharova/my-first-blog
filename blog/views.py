from django.utils import timezone
from .models import Post, Test
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm, CommentForm, TestForm
from django.contrib.auth.decorators import login_required


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    return render(request, 'blog/news_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/news_page.html', {
        'post': post,
        'create_comment_form': CommentForm(),
    })


def tests(request):
    tests = Test.objects.all()
    return render(request, 'tests/tests.html', {'tests': tests})


def test(request, pk):
    test = get_object_or_404(Test, pk=pk)
    if request.method == "POST":
        pass
        # form = PostForm(request.POST, instance=post)
        # if form.is_valid():
        #     post = form.save(commit=False)
        #     post.author = request.user
        #
        #     post.save()
        #     return redirect('postst_detail', pk=post.pk)
    else:
        form = TestForm()

    # return render(request, 'blog/post_edit.html', {'form': form})

    return render(request, 'tests/test.html', {'test': test, 'form': form})


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
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post_pk = pk
        comment.save()
    return redirect('blog/news_page.html', pk)

@login_required
def profile(request, pk):
    user = get_object_or_404(User, username=username)
    tests = Test.objects.all()
    return render(request, 'profile.html', {
        'user': user,
        'tests': tests.filter(assignee=user),
    })


# def add_comment_to_post(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     if request.method == "POST":
#         form = CommentForm(request.POST)
#         if form.is_valid():
#             comment = form.save(commit=False)
#             comment.post = post
#             comment.save()
#             return redirect('post_detail', pk=post.pk)
#     else:
#         form = CommentForm()
#     return render(request, 'blog/add_comment_to_post.html', {'form': form})
# Create your views here.


