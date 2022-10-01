from django.contrib import admin

from .models import Group, Post

EMPTY_VALUE_DISPLAY = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "description")
    empty_value_display = EMPTY_VALUE_DISPLAY


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author", "group")
    list_editable = ("group",)
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = EMPTY_VALUE_DISPLAY


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
