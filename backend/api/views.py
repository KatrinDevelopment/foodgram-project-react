from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Exists, OuterRef
from djoser.views import UserViewSet as CustomUserView
from requests import Response
from rest_framework import filters, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action

from api import serializers
from recipes.models import (Favorite, Ingredient, RecipeIngredients, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow, User
from .filters import RecipeFilter, IngredientFilter
from .permissions import AdminOrReadOnly, AuthorOrReadOnly
from .pagination import LimitPagePagination


class UserViewSet(CustomUserView):
    queryset = User.objects.all()
    serializer_class = serializers.CustomUserSerializer
    pagination_class = LimitPagePagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('username', 'email')
    permission_classes = (AllowAny, )

    def get_queryset(self):
        return User.objects.all()

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        user = get_object_or_404(User, username=request.user)
        if request.method == 'POST':
            serializer = serializers.FollowSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = get_object_or_404(
            Follow, user=user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        pages = self.paginate_queryset(User.objects.filter(subscribe__user=request.user))
        serializer = serializers.FollowSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = None
    permission_classes = (AdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    permission_classes = (AuthorOrReadOnly, )
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        return (
            Recipe.objects.all().annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        recipe=OuterRef('pk'), user=user.pk
                    )
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        recipe=OuterRef('pk'), user=user.pk)
                )
            )
        )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.RecipeSerializer
        return serializers.RecipePostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def add_to(serializer_class, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = serializer_class(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def del_from(model, request, pk):
        get_object_or_404(
            model,
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated],
            url_path='favorite')
    def favorites(self, request, pk):
        if request.method == 'POST':
            return self.add_to(serializers.FavoriteSerializer, request, pk)
        return self.del_from(Favorite, request, pk)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated],
            url_path='shopping_cart')
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to(serializers.ShoppingCartSerializer, request, pk)
        return self.del_from(ShoppingCart, request, pk)

    @staticmethod
    def download_shopping_cart(ingredients):
        shopping_list = 'Список покупок:'
        for ingredient in ingredients:
            shopping_list += (
                f'\n{ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]}) - '
                f'{ingredient["amount"]}'
            )
        filename = 'shopping_cart.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename = {filename}'
        return response

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated],
            url_path='download_shopping_cart')
    def make_shopping_list(self, request):
        ingredients = RecipeIngredients.objects.filter(
            recipe__shopping_cart__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return self.download_shopping_cart(ingredients)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    pagination_class = None
    permission_classes = (AdminOrReadOnly,)
    filter_backends = [IngredientFilter]
