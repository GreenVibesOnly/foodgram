from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ModifiedUserViewSet

app_name = 'users'

router = DefaultRouter()

router.register('users', ModifiedUserViewSet)
router.register('users/me/avatar', ModifiedUserViewSet, basename='avatar')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
