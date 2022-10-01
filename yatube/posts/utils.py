from django.conf import settings as st
from django.core.paginator import Paginator


def paginator_posts(post_list, request):
    paginator = Paginator(post_list, st.POST_LIMIT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj
