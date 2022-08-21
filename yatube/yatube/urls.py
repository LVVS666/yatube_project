from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('post.urls', namespace="posts")),
    path('admin/', admin.site.urls),
]