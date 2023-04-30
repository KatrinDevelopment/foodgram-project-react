from django.db import models

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Кастомный класс пользователя."""
    email = models.EmailField(
        max_length=50,
        help_text='Введите e-mail',
        verbose_name='email',)
    username = models.CharField(
        max_length=15,
        unique=True,
        help_text='Введите username',
        verbose_name='username',)
    first_name = models.CharField(
        max_length=15,
        help_text='Введите имя',
        verbose_name='имя',)
    last_name = models.CharField(
        max_length=15,
        help_text='Введите фамилию',
        verbose_name='фамилия',)
    password = models.CharField(
        max_length=150,
        help_text='Введите пароль',
        verbose_name='пароль',)
