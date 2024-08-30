from django.conf import settings
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import (IntegerField, ReadOnlyField,
                                   SerializerMethodField)
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from users.serializers import ModifiedUserSerializer
from .models import (Ingredient, Recipe, RecipeIngredient, ShortLink, Tag)

User = get_user_model()


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(ModelSerializer):
    id = IntegerField(write_only=True)
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = IntegerField(
        max_value=settings.MIN_MODEL_VALUE,
        min_value=settings.MAX_MODEL_VALUE
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSubscribeSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class RecipeReadSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = ModifiedUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context.request.user
        if user.is_anonymous:
            return False
        return user.favorites_recipes.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.request.user
        if user.is_anonymous:
            return False
        return user.shopping_cart_recipes.filter(recipe=obj).exists()


class RecipeWriteSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = ModifiedUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True)
    image = Base64ImageField()
    cooking_time = IntegerField(
        max_value=settings.MIN_MODEL_VALUE,
        min_value=settings.MAX_MODEL_VALUE
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError('Добавьте хотя бы один тег')
        tags_list = [tag.id for tag in tags]
        if len(tags_list) != len(set(tags_list)):
            raise ValidationError('Теги не должны повторяться')
        return value

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError('Добавьте хотя бы один ингредиент')
        ingredient_list = [ingredient['id'] for ingredient in ingredients]
        if len(ingredient_list) != len(set(ingredient_list)):
            raise ValidationError(
                'Ингредиенты не должны повторяться.'
            )
        return value

    def validate_cooking_time(self, value):
        cooking_time = value
        if not cooking_time:
            raise ValidationError('Добавьте время приготовления')
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            )
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class ShortLinkSerializer(ModelSerializer):
    recipe = RecipeReadSerializer(read_only=True)

    class Meta:
        model = ShortLink
        fields = '__all__'
