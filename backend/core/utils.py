from django.conf import settings
from django.core.paginator import Page, Paginator
from django.db.models import QuerySet
from django.http import HttpRequest


def paginate(
    request: HttpRequest,
    queryset: QuerySet,
    posts_number: int = settings.PAGE_SIZE,
) -> Page:
    return Paginator(queryset, posts_number).get_page(request.GET.get('page'))


def truncatechars(
    text: str,
    string_truncate_num: int = settings.STRING_TRUNCATE_NUM,
) -> str:
    return (
        text[:string_truncate_num] + '…'
        if len(text) > string_truncate_num
        else text
    )
