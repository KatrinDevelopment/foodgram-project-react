from http import HTTPStatus

from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseServerError,
)
from django.shortcuts import render


def page_not_found(
    request: HttpRequest,
    exception: Exception,
) -> HttpResponseNotFound:
    del exception
    return render(
        request,
        'core/404.html',
        {
            'path': request.path,
        },
        status=HTTPStatus.NOT_FOUND,
    )


def csrf_failure(request: HttpRequest, reason='') -> HttpResponse:
    del reason
    return render(request, 'core/403csrf.html')


def internal_server_error(request: HttpRequest) -> HttpResponseServerError:
    return render(request, 'core/500.html', HTTPStatus.INTERNAL_SERVER_ERROR)
