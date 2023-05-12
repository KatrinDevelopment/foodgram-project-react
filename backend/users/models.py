from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        'email',
        max_length=254,
        help_text='Введите e-mail',
        unique=True,
    )
    username = models.CharField(
        'уникальный юзернейм',
        max_length=150,
        unique=True,
        help_text='Введите username',
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        help_text='Введите имя',
    )
    last_name = models.CharField(
        'фамилия',
        max_length=150,
        help_text='Введите фамилию',
    )
    password = models.CharField(
        'пароль', max_length=150, blank=False, help_text='Введите пароль',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'), name='unique_username_email',
            ),
        ]

    def __str__(self):
        return f'{self.username}: {self.first_name}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='подписчик',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    following = models.ForeignKey(
        User,
        verbose_name='автор для подписок',
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_follow',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.following}'
