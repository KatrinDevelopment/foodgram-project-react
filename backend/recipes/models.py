from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text='Введите название тега',
        verbose_name='название тега',
    )
    color = models.CharField(
        max_length=7,
        help_text='Введите цвет в HEX',
        verbose_name='цвет в HEX',
        blank=True,
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text='Введите тег',
        verbose_name='тег',
        blank=True,
        allow_unicode=True,
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        help_text='Введите название ингредиента',
        verbose_name='название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=50,
        help_text='Введите единицу измерения',
        verbose_name='единица измерения',
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit',
            ),
        ]

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='автор',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='список ингредиентов',
        help_text='Введите список ингредиентов',
        related_name='recipes',
        through='RecipeIngredients',
    )
    tags = models.ManyToManyField(
        Tag,
        help_text='Введите таг для рецепта',
        verbose_name='таг рецепта',
    )
    image = models.ImageField(
        verbose_name='изображение блюда',
        blank=True,
        null=True,
        help_text='Добавьте картинку блюда',
        upload_to='app/media/images/',
    )
    name = models.CharField(
        max_length=200,
        help_text='Введите название рецепта',
        verbose_name='название рецепта',
    )
    text = models.TextField(
        help_text='Введите текст рецепта',
        verbose_name='текст рецепта',
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text='Введите время приготовления в минутах',
        verbose_name='время приготовления в мин.',
    )
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return f'{self.name} {self.text}'


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipe_ingredients',
        verbose_name='ингредиент',
    )
    amount = models.IntegerField(
        verbose_name='количество в рецепте',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.recipe}, {self.ingredient}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='рецепт',
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite',
            ),
        ]

    def __str__(self):
        return f'{self.user}, {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='рецепт',
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shoppingcart',
            ),
        ]

    def __str__(self):
        return f'{self.recipe} {self.user}'
