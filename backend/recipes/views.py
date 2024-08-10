from datetime import datetime
import random
import string

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from core.filters import IngredientFilter, RecipeFilter
from core.pagination import ModifiedPagination
from core.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .models import (Favorite, Ingredient, RecipeIngredient, Recipe,
                     ShoppingCart, ShortLink, Tag)
from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeSubscribeSerializer, RecipeWriteSerializer,
                          ShortLinkSerializer, TagSerializer)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = ModifiedPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def add_resipe(self, model, user, pk, location_name):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(f'Рецепт уже есть в {location_name}',
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeSubscribeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_resipe(self, model, user, pk, location_name):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(f'Рецепта нет в {location_name}',
                        status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        location_name = 'избранном'
        if request.method == 'POST':
            return self.add_resipe(Favorite, request.user, pk,
                                   location_name)
        else:
            return self.delete_resipe(Favorite, request.user,
                                      pk, location_name)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        location_name = 'корзине покупок'
        if request.method == 'POST':
            return self.add_resipe(ShoppingCart, request.user, pk,
                                   location_name)
        else:
            return self.delete_resipe(ShoppingCart, request.user,
                                      pk, location_name)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not ShoppingCart.objects.filter(user=user).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients_list = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        today = datetime.today()
        shopping_list = (
            f'Список покупок дня: {today:%d-%m-%Y}\n\n'
        )
        shopping_list += '\n'.join([
            f'• {ingredient["ingredient__name"]} '
            f'- {ingredient["amount"]} '
            f'{ingredient["ingredient__measurement_unit"]}'
            for ingredient in ingredients_list
        ])
        shopping_list += (
            '- любовь - 1 горсточка ❤'
            '\n\n\n\n©Foodgram'
        )

        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response

    @action(
        detail=True
    )
    def short_link(self, request, short_url):
        recipe = get_object_or_404(ShortLink, short_link=short_url)
        full_link = (f'{self.request.scheme}://{self.request.get_host()}'
                     f'/recipes/{str(recipe.recipe_id)}')
        return redirect(full_link)


class ShortLinkViewSet(ModelViewSet):
    queryset = ShortLink.objects.all()
    serializer_class = ShortLinkSerializer

    @action(
        detail=True,
        url_path='get-link'
    )
    def short_link(self, request, pk):
        if not ShortLink.objects.filter(recipe__id=pk).exists():
            short_link = ''.join(random.choice(
                string.ascii_lowercase + string.digits) for _ in range(3))
            recipe = get_object_or_404(Recipe, id=pk)
            ShortLink.objects.create(recipe=recipe, short_link=short_link)
        short_link_obj = get_object_or_404(ShortLink, recipe_id=pk)
        base_link = f'{self.request.scheme}://{self.request.get_host()}/s/'
        short_link = str(base_link + short_link_obj.short_link)
        return Response({"short-link": short_link})
