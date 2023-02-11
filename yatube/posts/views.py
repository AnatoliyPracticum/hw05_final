from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, User, Group, Follow
from .forms import PostForm, CommentForm
from .utils import post_paginator


def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    post_list = Post.objects.all()
    page_obj = post_paginator(request, post_list)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = post_paginator(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    # Здесь код запроса к модели и создание словаря контекста
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list_profile = author.posts.all()
    page_obj = post_paginator(request, post_list_profile)
    posts_count = post_list_profile.count
    profile_fullname = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated:
        try:
            Follow.objects.get(user=request.user, author=author)
            following = True
        except Follow.DoesNotExist:
            following = False
    context = {
        'username': profile_fullname,
        'page_obj': page_obj,
        'posts_count': posts_count,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    posts_count = post.author.posts.all().count
    comments = post.comments.all()
    context = {
        'post': post,
        'posts_count': posts_count,
        'comment_form': CommentForm(),
        'comments': comments
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    if not form.is_valid():
        return render(
            request,
            template,
            {'form': form, 'is_edit': False}
        )

    post = form.save(commit=False)
    post.author = request.user
    post.save()

    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if not form.is_valid():
        context = {
            'post': post,
            'form': form,
            'is_edit': True
        }
        return render(
            request,
            template,
            context
        )
    # post = form.save(commit=False)
    post.save()

    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    template = 'posts/follow.html'
    title = 'Последние обновления избранных авторов'
    follow_posts_list = Post.objects.filter(
        author__following__user=request.user)
    page_obj = post_paginator(request, follow_posts_list)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    follow_author = get_object_or_404(User, username=username)
    if follow_author != request.user and (
        not request.user.follower.filter(author=follow_author).exists()
    ):
        Follow.objects.create(
            user=request.user,
            author=follow_author
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    follow_author = get_object_or_404(User, username=username)
    Follow.objects.get(
        user=request.user,
        author=User.objects.get(username=follow_author),
    ).delete()
    return redirect('posts:profile', username)
