from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
# from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm


POSTS_LIST: int = 10  # Количество постов выводимых на странице


# Главная страница
# @cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_LIST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


# Страница с группами публикаций

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, POSTS_LIST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


# Профайл пользователя

def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list_user = author.posts.all()
    paginator = Paginator(post_list_user, POSTS_LIST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # f = Follow.objects.filter(user=a).filter(author=auth).exists()
    following = Follow.objects.filter(
        user=request.user,
        author=author,
    ).exists()
    context = {
        'page_obj': page_obj,
        'author': author,
        'post_list_user': post_list_user,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


# Детальный просмотр отдельного поста
def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


# Создание поста
@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return redirect("posts:profile", request.user.username)
    return render(request, 'posts/create_post.html', {'form': form})


# Редактирование поста
@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.id)

    form = PostForm(
        request.POST or None,
        instance=post,
        files=request.FILES or None,
    )
    context = {'form': form, 'is_edit': True}

    if form.is_valid():
        form.save()

        return redirect('posts:post_detail', post_id=post.id)
    return render(request, 'posts/create_post.html', context)


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
    follow_post_list = Post.objects.filter(
        author__following__user=request.user
    )

    paginator = Paginator(follow_post_list, POSTS_LIST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if not Follow.objects.filter(
            user=user
    ).filter(
        author=author
    ).exists():
        if user == author:
            return redirect('posts:profile', username=username)
        Follow.objects.create(
            user=user,
            author=author,
        )
        return redirect('posts:profile', username=username)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    follow = Follow.objects.filter(
        user=user,
        author=author,
    )
    follow.delete()

    return redirect('posts:profile', username=username)
