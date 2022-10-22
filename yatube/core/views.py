from django.shortcuts import render
from http import HTTPStatus as ht


def page_not_found(request, exception):
    return render(request, 'core/404.html', {'path': request.path},
                  status=ht.NOT_FOUND
                  )


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')


def server_error(request):
    return render(request, 'core/500.html', status=ht.INTERNAL_SERVER_ERROR)


def permission_denied(request, exception):
    return render(request, 'core/403.html', status=ht.FORBIDDEN)
