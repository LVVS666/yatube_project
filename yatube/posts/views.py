# Create your views here.
# ice_cream/views.py
from django.shortcuts import render, get_object_or_404
from .models import Post, Group

POSTS_LIMIT = 10


# Главная страница
def index(request):
    posts = Post.objects.order_by("-pub_date")[:POSTS_LIMIT]
    context = {
        "posts": posts,
    }
    return render(request, "posts/index.html", context)


# Посты отфильтрованные по группам
def group_posts(request, slug):

    group = get_object_or_404(Group, slug=slug)

    posts = Post.objects.filter(group=group).order_by("-pub_date")[:10]
    context = {
        "group": group,
        "posts": posts,
    }
    return render(request, "posts/group_list.html", context)
