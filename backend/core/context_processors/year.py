from typing import Dict

from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone


def year(request: WSGIRequest) -> Dict[str, int]:
    return {
        'year': timezone.now().year,
    }
