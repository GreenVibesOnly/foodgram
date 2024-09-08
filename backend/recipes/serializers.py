from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import (IntegerField, SerializerMethodField)
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


class IngredientInRecipeReadSerializer(ModelSerializer):
    id = SerializerMethodField()
    name = SerializerMethodField()
    measurement_unit = SerializerMethodField()
    amount = SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_id(self, obj):
        ingredient_recipe = RecipeIngredient.objects.filter(
            ingredient=obj).first()
        return f'{ingredient_recipe.ingredient.id}'

    def get_name(self, obj):
        ingredient_recipe = RecipeIngredient.objects.filter(
            ingredient=obj).first()
        return f'{ingredient_recipe.ingredient.name}'

    def get_measurement_unit(self, obj):
        ingredient_recipe = RecipeIngredient.objects.filter(
            ingredient=obj).first()
        return f'{ingredient_recipe.ingredient.measurement_unit}'

    def get_amount(self, obj):
        ingredient_recipe = RecipeIngredient.objects.filter(
            ingredient=obj).first()
        return f'{ingredient_recipe.amount}'


class IngredientInRecipeWriteSerializer(ModelSerializer):
    id = IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


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
    ingredients = IngredientInRecipeReadSerializer(many=True, read_only=True)
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
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorites_recipes.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.shopping_cart_recipes.filter(recipe=obj).exists()


class RecipeWriteSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = ModifiedUserSerializer(read_only=True)
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    image = Base64ImageField()
    cooking_time = IntegerField(
        max_value=settings.MAX_MODEL_VALUE,
        min_value=settings.MIN_MODEL_VALUE
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
        ingredients_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError('Ингридиенты не могут повторяться!')
            ingredients_list.append(ingredient)
        return value

    def validate_cooking_time(self, value):
        cooking_time = value
        if not cooking_time:
            raise ValidationError('Добавьте время приготовления')
        return value

    def bulk_create_ingredients(self, ingredients, recipe):
        bulk_list = []
        for ingredient in ingredients:
            bulk_list.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient_id=ingredient.get('id'),
                    amount=ingredient.get('amount')
                )
            )
        return RecipeIngredient.objects.bulk_create(bulk_list)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.bulk_create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        self.bulk_create_ingredients(ingredients, instance)
        instance.tags.clear()
        instance.tags.set(tags)
        return super().update(instance, validated_data)

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
