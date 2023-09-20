from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from posts.forms import CommentForm, PostForm
from posts.models import Comment, Follow, Group, Post, User
from posts.utils import paginator

N_POST = 10
CACHE_TIME = 20


@cache_page(CACHE_TIME)
def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    page_obj = paginator(request, post_list, N_POST)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group)
    page_obj = paginator(request, post_list, N_POST)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated:
        if request.user.follower.filter(author=author):
            following = True
    post_list = author.posts.all()
    page_obj = paginator(request, post_list, N_POST)
    template = 'posts/profile.html'
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post)
    form = CommentForm(
        request.POST or None,
    )
    template = 'posts/post_detail.html'
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author_id = request.user.id
            post.save()
            return redirect('posts:profile', request.user.username)
    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        instance=post,
        files=request.FILES or None,
    )
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)

    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    follower = Follow.objects.filter(user=request.user).values('author')
    post_list = Post.objects.filter(author__in=follower)
    page_obj = paginator(request, post_list, N_POST)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    if request.user.username != username:
        Follow.objects.get_or_create(
            user=request.user,
            author=get_object_or_404(User, username=username)
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    if Follow.objects.filter(author=author).exists():
        Follow.objects.filter(author=author).delete()
    return redirect('posts:profile', username=username)
