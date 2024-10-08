from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from .models import Subscribe


User = get_user_model()


class AvatarSerializer(ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class ModifiedUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.subscriber.filter(author=obj).exists()


class ModifiedUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError(
                'Этот адрес электронной почты уже используется'
            )
        return value


class SubscribeSerializer(ModifiedUserSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta(ModifiedUserSerializer.Meta):
        fields = ModifiedUserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        from recipes.serializers import RecipeSubscribeSerializer
        request = self.context['request']
        limit = request.GET['recipes_limit']
        recipes = obj.authored_recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSubscribeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.authored_recipes.count()


class SubscribeWriteSerializer(ModifiedUserSerializer):
    author = ModifiedUserSerializer(read_only=True)
    user = ModifiedUserSerializer(read_only=True)

    class Meta:
        model = Subscribe
        fields = (
            'id',
            'author',
            'user'
        )

    def validate_author(self, value):
        author = value
        user = self.context['user']
        if user.subscriber.filter(author=author).exists():
            raise ValidationError(
                'Вы уже подписаны на этого автора',
                status=status.HTTP_400_BAD_REQUEST
            )
        if author == user:
            raise ValidationError(
                'Нельзя подписаться на самого себя',
                status=status.HTTP_400_BAD_REQUEST
            )
        return value
