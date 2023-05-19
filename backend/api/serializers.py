from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from core.utils import Base64ImageField
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Follow, User


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user,
            following=obj.pk,
        ).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


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
        model = RecipeIngredient
        fields = ('id', 'name', 'amount', 'measurement_unit')
        read_only_fields = (
            'id',
            'measurement_unit',
            'name',
        )


class IngredientsAmountSerializer(ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context.get('request').user
        if Favorite.objects.filter(recipe=self.instance, user=user).exists():
            raise serializers.ValidationError(
                detail='Рецепт уже в избранных',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data


class FollowSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'email',
            'username',
            'last_name',
            'first_name',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = RecipeInfoSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, author):
        return Recipe.objects.filter(author=author).count()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Follow.objects.filter(
                user=obj.user,
                following=obj.pk,
            ).exists()
        return False

    def validate(self, data):
        following = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(following=following, user=user).exists():
            raise serializers.ValidationError(
                detail='Подписка уже существует',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == following:
            raise serializers.ValidationError(
                detail='Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data


class RecipeSerializer(ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True,
        source='recipe_ingredients',
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField(max_length=None)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and obj.favorite.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe__id=obj.id,
        ).exists()

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipePostSerializer(ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        allow_empty=False,
    )
    ingredients = IngredientsAmountSerializer(many=True)
    image = Base64ImageField(
        max_length=None,
        required=True,
        use_url=True,
    )

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def validate_ingredients(self, ingredients):
        ingredients_list = []
        if not ingredients:
            raise serializers.ValidationError('Не выбраны ингредиенты')
        for ingredient in ingredients:
            if ingredient['id'] in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальными',
                )
            ingredients_list.append(ingredient['id'])
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError('Не выбраны теги для рецепта')
        for tag in tags:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError(
                    'Указанного тега не существует',
                )
        return tags

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 1 мин.',
            )
        return cooking_time

    def update_create_recipe(self, validated_data, instance=None):
        tag_list = validated_data.pop('tags', None)
        ingredient_list = validated_data.pop('ingredients', None)
        if not instance:
            instance = super().create(validated_data)
        else:
            super().update(instance, validated_data)
            instance.ingredients.clear()
            instance.tags.clear()

        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=instance,
                    ingredient=ingredient_item['id'],
                    amount=ingredient_item['amount'],
                )
                for ingredient_item in ingredient_list
            ],
        )
        instance.tags.set(tag_list)
        return instance

    def create(self, validated_data):
        return self.update_create_recipe(validated_data)

    def update(self, instance, validated_data):
        return self.update_create_recipe(validated_data, instance=instance)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={'request': self.context.get('request')},
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe'],
            ),
        ]

    def to_representation(self, instance):
        return RecipeInfoSerializer(instance.recipe).data


class ShoppingCartSerializer(ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['user', 'recipe'],
            ),
        ]

    def to_representation(self, instance):
        return RecipeInfoSerializer(instance.recipe).data
