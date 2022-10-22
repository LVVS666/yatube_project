from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow
from .utils import paginator_return_page


def index(request):
    template = "posts/index.html"
    posts = Post.objects.all().select_related("author", "group")
    context = {
        "page_obj": paginator_return_page(posts, request),
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = "posts/group_list.html"
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {
        "group": group,
        "page_obj": paginator_return_page(posts, request),
    }
    return render(request, template, context)


def profile(request, username):
    template = "posts/profile.html"
    user = User.objects.get(username=username)
    posts = user.posts.select_related("group")
    post_count = posts.count()
    if request.user.is_authenticated:
        following = request.user.follower.filter(author=user).exists()
    else:
        following = False
    context = {
        "post_count": post_count,
        "author": user,
        "page_obj": paginator_return_page(posts, request),
        "following": following,
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
        "form": CommentForm(),
        "comments": post.comment.all(),

    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = "posts/create_post.html"
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    )
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
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post
                    )
    if request.user != post.author:
        return redirect("posts:post_detail", post_id=post_id)
    if form.is_valid():
        post.save()
        return redirect("posts:post_detail", post_id=post_id)
    context = {"form": form, "is_edit": True}
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
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    template = "posts/follow.html"
    posts = Post.objects.filter(author__following__user=request.user)
    context = {
        "page_obj": paginator_return_page(posts, request),
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
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
    follow_author = get_object_or_404(User, username=username)
    data_follow = request.user.follower.filter(author=follow_author)
    if data_follow.exists():
        data_follow.delete()
    return redirect("posts:profile", username)
