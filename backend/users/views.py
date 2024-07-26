from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.pagination import ModifiedPagination
from core.permissions import IsUserOrReadOnly, IsAdminOrReadOnly
from .models import Subscribe
from .serializers import (AvatarSerializer,
                          ModifiedUserSerializer,
                          ModifiedUserCreateSerializer,
                          SubscribeSerializer)


User = get_user_model()


class ModifiedUserViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (IsUserOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = ModifiedPagination

    def get_serializer_class(self):
        #if self.action == 'subscribe':
        #    return SubscribeSerializer
        if self.request.method == 'POST':
            return ModifiedUserCreateSerializer
        return ModifiedUserSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=self.kwargs.get('id'))

        if request.method == 'POST':
            if Subscribe.objects.filter(user=user, subscriber=author).exists():
                raise ValidationError(
                    'Вы уже подписаны на этого автора', code=400
                )
            if user == author:
                raise ValidationError(
                    'Нельзя подписаться на самого себя', code=400
                )
            serializer = SubscribeSerializer(author,
                                             context={"request": request})
            Subscribe.objects.create(user=user, subscriber=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(Subscribe,
                                             user=user,
                                             subscriber=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get', ],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        #user = request.user
        #queryset = User.objects.filter(subscribing__user=user)
        #pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            #pages,
            many=True,
            context={'request': request}
        )
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
            return Response(serializers.data, status=200)
        user.avatar = None
        user.save()
        return Response(status=204)
