from django.db import models
from django.core.validators import MinValueValidator

from core.utils import truncatechars
from users.models import User


class Tag(models.Model):
    name = models.SlugField(
        unique=True,
        help_text='Введите название тега',
        verbose_name='название тега',
    )
    color = models.CharField(max_length=9)
    slug = models.SlugField(
        unique=True,
        help_text='Введите тег',
        verbose_name='тег',
    )


class Ingredients(models.Model):
    name = models.CharField(
        max_length=200,
        help_text='Введите название ингредиента',
        verbose_name='название ингредиента',)
    amount = models.IntegerField()
    measurement_unit = models.CharField(
        max_length=10,
        help_text='Введите единицу измерения',
        verbose_name='единица измерения',)

    def __str__(self) -> str:
        return truncatechars(self.name)


class Recept(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='автор',
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        Ingredients,
        verbose_name='автор',
        on_delete=models.CASCADE,
    )
    tags = models.SlugField(
        unique=True,
        help_text='Введите таг для ингредиента',
        verbose_name='таг ингредиента',
    )
    image = models.TextField(
        'картинка',
        blank=True,
        help_text='Добавьте картинку',
    )
    name = models.CharField(
        max_length=200,
        help_text='Введите название рецепта',
        verbose_name='название рецепта',)
    text = models.TextField(
        help_text='Введите текст рецепта',
        verbose_name='текст рецепта',
    )
    cooking_time = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self) -> str:
         return truncatechars(self.name)



