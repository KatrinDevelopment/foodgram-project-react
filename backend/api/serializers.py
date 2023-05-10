from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import (
    ModelSerializer,
    SlugRelatedField,
)
from rest_framework import serializers, status
from rest_framework.validators import UniqueTogetherValidator

from core.utils import Base64ImageField
from recipes.models import ShoppingCart, Tag, Recipe, Ingredient, RecipeIngredients, Favorite
from users.models import Follow, User


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj.pk).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class FollowSerializer(ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'author'],
                message='Вы уже подписаны на этого автора.'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        self.context['subscriptions'] = set(
            Follow.objects.filter(
                user_id=request.user.id).values_list('author_id', flat=True))
        return FollowSerializer(
            instance.author, context=self.context).data


class IngredientSerializer(ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeIngredientsSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all(),
    )
    measurement_unit = SlugRelatedField(
        source='ingredient',
        slug_field='measurement_unit',
        read_only=True,
    )
    name = SlugRelatedField(
        source='ingredient',
        slug_field='name',
        read_only=True,
    )

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'name',
            'amount',
            'measurement_unit'
        )
        read_only_fields = ('id', 'measurement_unit', 'name',)


class RecipeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowListSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )
        read_only_fields = ('email', 'username', 'last_name', 'first_name',)

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = RecipeInfoSerializer(
            recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, author):
        return Recipe.objects.filter(author=author).count()

    def get_is_subscribed(self, author):
        return Follow.objects.filter(
            user=self.context.get('request').user,
            author=author
        ).exists()

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError(
                detail='Подписка уже существует',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise serializers.ValidationError(
                detail='Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data


class RecipeSerializer(ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True, source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField(max_length=None)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and obj.favorites.filter(user=request.user).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and obj.shopping_cart.filter(user=request.user).exists())

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipePostSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)
    ingredients = RecipeIngredientsSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def create_ingredients(self, ingredients, recipe):
        RecipeIngredients.objects.bulk_create([RecipeIngredients(
            recipe=recipe,
            ingredient_id=ingredient['ingredient']['id'],
            amount=ingredient.get('amount')) for ingredient in ingredients
        ])

    def validate_amount(self, value):
        if int(value) < 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 1')
        return value

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 1 мин.')
        return cooking_time

    def update_or_create_recipe(self, validated_data, instance=None):
        tag_list = validated_data.pop('tags', None)
        ingredient_list = validated_data.pop('ingredients', None)
        if not (tag_list or ingredient_list):
            raise serializers.ValidationError(
                'Укажите как минимум один тег и ингредиент'
            )
        if not instance:
            instance = Recipe()
        for key, val in validated_data.items():
            setattr(instance, key, val)
        instance.save()
        instance.ingredients.clear()
        instance.tags.clear()
        for ingredient in ingredient_list:
            RecipeIngredients.objects.create(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        instance.tags.set(tag_list)
        return instance

    def create(self, validated_data):
        return self.update_or_create_recipe(validated_data)

    def update(self, instance, validated_data):
        return self.update_or_create_recipe(validated_data, instance=instance)

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance)
        return serializer.data


class SubscriptionRecipeSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)

    def validate(self, data):
        recipe = self.instance
        user = self.context.get('request').user
        if Favorite.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                detail='Рецепт уже в избранных',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe'],
            )
        ]

    def to_representation(self, instance):
        return RecipeInfoSerializer(instance.recipe).data


class ShoppingCartSerializer(ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['user', 'recipe'],
            )
        ]

    def to_representation(self, instance):
        return FollowSerializer(instance.recipe).data
