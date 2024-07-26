from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet,
                    ShortLinkViewSet, TagViewSet)

app_name = 'recipes'

router = DefaultRouter()

router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('recipes', ShortLinkViewSet)

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^(?P<short_url>\w{3})/$',
            RecipeViewSet.as_view({'get': 'short_link'})),
]
