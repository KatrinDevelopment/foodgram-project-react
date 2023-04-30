from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from core.utils import truncatechars

User = get_user_model()


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату публикации, автора."""

    text = models.TextField(
        help_text='Введите текст',
        verbose_name='текст',
    )
    pub_date = models.DateTimeField(
        'дата и время публикации',
        auto_now_add=True,
        db_index=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name='автор',
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return truncatechars(self.text, settings.STRING_TRUNCATE_NUM)

    class Meta:
        abstract = True
        ordering = ('-pub_date',)
