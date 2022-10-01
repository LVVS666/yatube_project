from django.conf import settings as st
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User
from .utils import paginator_posts


def index(request):
    template = "posts/index.html"
    posts = Post.objects.all().select_related("author", "group")
    paginator = Paginator(posts, st.POST_LIMIT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = "posts/group_list.html"
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, st.POST_LIMIT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = "posts/profile.html"
    user = User.objects.get(username=username)
    posts = user.posts.select_related("group")
    post_count = posts.count()
    context = {
        "post_count": post_count,
        "author": user,
        "page_obj": paginator_posts(posts, request),
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = "posts/post_detail.html"
    post = get_object_or_404(Post, id=post_id)
    post_count = post.author.posts.count()
    context = {
        "post": post,
        "post_count": post_count,
        "post_id": post_id,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = "posts/create_post.html"
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", username=post.author)
    context = {"form": form, "is_edit": False}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = "posts/create_post.html"
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.user != post.author:
        return redirect("posts:post_detail", post_id=post_id)
    if form.is_valid():
        post.save()
        return redirect("posts:post_detail", post_id=post_id)
    context = {"form": form, "is_edit": True}
    return render(request, template, context)
