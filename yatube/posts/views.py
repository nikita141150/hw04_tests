from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm
from .models import Post, Group, User


def pagination(request, post_list):
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': pagination(request, Post.objects.all()), })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = {
        'group': group,
        'page_obj': pagination(request, post_list),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    context = {
        'author': author,
        'page_obj': pagination(request, post_list),
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    ed_post = form.save(commit=False)
    ed_post.author = request.user
    ed_post.save()
    return redirect('posts:profile', username=request.user)


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, pk=post_id, author=request.user)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post.pk)
    form = PostForm(request.POST or None, instance=post)
    if not form.is_valid():
        return render(
            request, 'posts/create_post.html',
            {'form': form, 'is_edit': is_edit, 'post': post}
        )
    form.save()
    return redirect('posts:post_detail', post_id=post.pk)
