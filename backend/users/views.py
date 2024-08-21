from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.pagination import ModifiedPagination
from core.permissions import IsAdminOrReadOnly, IsUserOrReadOnly

from .models import Subscribe
from .serializers import (AvatarSerializer, ModifiedUserCreateSerializer,
                          ModifiedUserSerializer, SubscribeSerializer)

User = get_user_model()


class ModifiedUserViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (IsUserOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = ModifiedPagination

    def get_serializer_class(self):
        if self.action == 'subscriptions':
            return SubscribeSerializer
        elif self.request.method == 'POST':
            return ModifiedUserCreateSerializer
        return ModifiedUserSerializer

    @action(detail=False,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def set_password(self, request, *args, **kwargs):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request})
        if serializer.is_valid(raise_exception=True):
            self.request.user.set_password(serializer.data['new_password'])
            self.request.user.save()
            return Response('Пароль успешно изменен',
                            status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=self.kwargs.get('id'))

        if request.method == 'POST':
            if Subscribe.objects.filter(user=user, author=author).exists():
                raise ValidationError(
                    'Вы уже подписаны на этого автора', code=400
                )
            if user == author:
                raise ValidationError(
                    'Нельзя подписаться на самого себя', code=400
                )
            serializer = SubscribeSerializer(
                author, context={'request': request}
            )
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscribe, user=user, author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(author__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(pages,
                                         many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['put', 'delete'])
    def avatar(self, request, **kwargs):
        user = request.user
        if request.method == 'PUT':
            serializers = AvatarSerializer(user, data=request.data)
            serializers.is_valid(raise_exception=True)
            serializers.save()
            return Response(serializers.data)
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
