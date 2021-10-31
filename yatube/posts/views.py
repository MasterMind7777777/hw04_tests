from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group
from .forms import PostForm
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


def paginator_my(request, post_list):
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    post_list = Post.objects.all()
    page_obj = paginator_my(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = Group.objects.get(slug=slug)
    post_list = group.posts.all()
    page_obj = paginator_my(request, post_list)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    full_name = author.get_full_name()

    post_list = author.posts.all()
    post_count = post_list.count()
    page_obj = paginator_my(request, post_list)

    context = {
        'page_obj': page_obj,
        'post_count': post_count,
        'full_name': full_name,
        'author': author,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = post.author

    full_name = author.get_full_name()
    post_count = author.posts.all().count()
    context = {
        'post': post,
        'author': author,
        'full_name': full_name,
        'post_count': post_count,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):

    form = PostForm(request.POST or None)
    context = {
        'form': form,
    }
    if form.is_valid() and request.method == 'POST':
        form_obj = form.save(commit=False)
        form_obj.author = request.user
        form_obj.save()
        return redirect('posts:profile', username=request.user)
    else:
        return render(request, 'posts/create_post.html', context)


def post_edit(request, post_id):

    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.pk)
    is_edit = True

    form = PostForm(request.POST or None, instance=post)
    context = {
        'form': form,
        'is_edit': is_edit,
    }
    if form.is_valid() and request.method == 'POST':
        form_obj = form.save(commit=False)
        form_obj.author = request.user
        form_obj.save()
        return redirect('posts:post_detail', post_id=post.pk)
    else:
        return render(request, 'posts/create_post.html', context)
