from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

POSTS_LIST: int = 10  # Количество постов выводимых на странице


def paginator(request, queryset):
    paginator = Paginator(queryset, POSTS_LIST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return {'page_obj': page_obj}


# Главная страница
def index(request):
    post_list = Post.objects.all()

    context = paginator(request, post_list)

    return render(request, 'posts/index.html', context)


# Страница с группами публикаций
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()

    context = {'group': group}
    context.update(paginator(request, post_list))

    return render(request, 'posts/group_list.html', context)


# Профайл пользователя
def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list_user = author.posts.all()
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user.id,
        author=author,
    ).exists()

    context = {
        'author': author,
        'post_list_user': post_list_user,
        'following': following,
    }
    context.update(paginator(request, post_list_user))
    return render(request, 'posts/profile.html', context)


# Детальный просмотр отдельного поста
def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
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

    context = paginator(request, follow_post_list)

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author and not Follow.objects.filter(
        user=user,
        author=author,
    ).exists():
        Follow.objects.create(
            user=user,
            author=author,
        )

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(
        user=user,
        author=author,
    )
    follow.delete()

    return redirect('posts:profile', username=username)
