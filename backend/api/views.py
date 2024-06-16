from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from io import BytesIO
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from blog.models import (Favourite, Ingredient, IngredientInRecipe, Recipe,
                         ShoppingCart, Tag)
from .filters import IngredientFilter, RecipeFilter
from .pagination import ModifiedPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeShortSerializer, RecipeWriteSerializer,
                          TagSerializer)


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
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_resipe(self, model, user, pk, location_name):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(f'Рецепта нет в {location_name}',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        location_name = 'избранном'
        if request.method == 'POST':
            return self.add_resipe(Favourite, request.user, pk)
        else:
            return self.delete_resipe(Favourite, request.user,
                                      pk, location_name)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        location_name = 'корзине покупок'
        if request.method == 'POST':
            return self.add_resipe(ShoppingCart, request.user, pk)
        else:
            return self.delete_resipe(ShoppingCart, request.user,
                                      pk, location_name)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        ingredients_list = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        buffer = BytesIO()
        file = canvas.Canvas('Foodgram_shopping_list.pdf')
        file.setFont('Times-Roman', 20)
        file.drawString(50, 50, 'Покупки дня')
        file.line(50, 100, 250, 100)
        file.drawImage('backend/media/shopping_list/fork_and_knife.png',
                       350, 50, width=50, height=50)
        str_point = 120
        file.setFont('Times-Roman', 15)
        for ingredient in ingredients_list:
            ingredient_name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['amount']
            file.drawString(50, str_point, f'- {ingredient_name}: '
                            f'{amount} {measurement_unit}')
            str_point += 20
        file.drawString(50, 800, 'Foodgram')
        file.save()
        buffer.seek(0)
        return FileResponse(
            buffer,
            as_attachment=True,
            filename='Foodgram_shopping_list.pdf'
        )
