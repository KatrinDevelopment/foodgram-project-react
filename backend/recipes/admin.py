from django.contrib import admin

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Follow, User

models = [
    Tag,
    Favorite,
    ShoppingCart,
]

admin.site.register(models)


class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = (
        'recipe',
        'ingredient',
    )
    list_filter = (
        'recipe',
        'ingredient',
    )
    empty_value_display = '-пусто-'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = (
        'username',
        'email',
    )
    list_filter = (
        'email',
        'first_name',
    )
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'following',
    )
    search_fields = (
        'following',
        'user',
    )
    list_filter = ('following',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'is_favorited')
    search_fields = ('author', 'name', 'tags')
    list_filter = ('author', 'name', 'tags')
    inlines = (RecipeIngredientInLine,)
    empty_value_display = '-пусто-'

    def is_favorited(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Ingredient)
class Ingredient(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
