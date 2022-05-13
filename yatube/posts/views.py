import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User

PATH_TO_INDEX = os.path.join('posts', 'index.html')
PATH_TO_GROUP_LIST = os.path.join('posts', 'group_list.html')
PATH_TO_PROFILE = os.path.join('posts', 'profile.html')
PATH_TO_POST = os.path.join('posts', 'post_detail.html')
PATH_TO_CREATE_POST = os.path.join('posts', 'create_post.html')
PATH_TO_FOLLOW = os.path.join('posts', 'follow.html')


def page_maker(post_list, request):
    """Return paginator."""
    paginator = Paginator(post_list, settings.POSTS_IN_PAGINATOR)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    """Returns main page."""
    template = PATH_TO_INDEX
    post_list = Post.objects.select_related(
        'group', 'author').all()
    title = 'Main page for project Yatube'
    context = {
        'title': title,
        'page_obj': page_maker(request=request, post_list=post_list),
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Returns group page."""
    template = PATH_TO_GROUP_LIST
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('group', 'author').all()
    context = {
        'group': group,
        'page_obj': page_maker(request=request, post_list=post_list)
    }
    return render(request, template, context)


def profile(request, username):
    """Model and the creation of the context dict for user."""
    template = PATH_TO_PROFILE
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group', 'author').all()
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author
    ).exists()
    context = {
        'author': author,
        'posts_count': author.posts.count(),
        'page_obj': page_maker(request=request, post_list=post_list),
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Model and the creation of the context dict for posts."""
    template = PATH_TO_POST
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    posts_count = author.posts.count()
    form = CommentForm(request.POST or None)
    comment = Comment.objects.filter(post_id=post.id)
    context = {
        'post': post,
        'posts_count': posts_count,
        'comments': comment,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Create a post by user."""
    template = PATH_TO_CREATE_POST
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)
    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """Edit a post by the author."""
    # groups = Group.objects.all()
    template = PATH_TO_CREATE_POST
    required_post = Post.objects.get(pk=post_id)
    if required_post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=required_post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {'form': form, 'required_post': required_post, 'is_edit': True}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Leave a comment on post."""
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
    """Returns follow page."""
    template = PATH_TO_FOLLOW
    post_list = Post.objects.filter(author__following__user=request.user)
    title = 'Page to follow author'
    context = {
        'title': title,
        'page_obj': page_maker(request=request, post_list=post_list),
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """How to follow the author."""
    user = get_object_or_404(User, username=username)
    if request.user != user:
        Follow.objects.get_or_create(
            user_id=request.user.id,
            author_id=user.id
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """How to unfollow the author."""
    user = get_object_or_404(User, username=username)
    Follow.objects.filter(user_id=request.user.id, author_id=user.id).delete()
    return redirect('posts:profile', username=username)
