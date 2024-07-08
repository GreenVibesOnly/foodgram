from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

app_name = 'recipes'

router = DefaultRouter()

router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('recipes/<int:pk>/get-link/', RecipeViewSet.as_view(
        {'get': 'get_short_link', })),
    path('', include(router.urls)),
]
