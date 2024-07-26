from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models


User = get_user_model()


class Tag(models.Model):

    name = models.CharField(
        'Название',
        unique=True,
        max_length=32
    )
    slug = models.SlugField(
        'Слаг',
        unique=True,
        null=True,
        max_length=32
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        'Название',
        max_length=128
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=64
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes_with_tag',
        verbose_name='Теги'
    )
    author = models.ForeignKey(
        User,
        related_name='authored_recipes',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Автор',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes_with_ingredient',
        verbose_name='Ингредиенты'
    )
    is_favorited = models.ManyToManyField(
        User,
        through='Favorite',
        related_name='favorite_recipes',
        verbose_name='В избранном'
    )
    is_in_shopping_cart = models.ManyToManyField(
        User,
        through='ShoppingCart',
        related_name='recipes_in_shopping_cart',
        verbose_name='В корзине'
    )
    name = models.CharField(
        'Название',
        max_length=256
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/images/'
    )
    text = models.TextField(
        'Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(
            1,
            message='Время приготовления не может быть меньше 1 минуты'
        )]
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_in_resipe',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes_w_ingredient',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return (
            f'{self.ingredient.name} '
            f'({self.ingredient.measurement_unit}) - {self.amount}'
        )


class Favorite(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites_recipes',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favourite')
        ]

    def __str__(self):
        return f'{self.user} {self.recipe} - favorites'


class ShoppingCart(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipes',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_shoppingcart')
        ]

    def __str__(self):
        return f'{self.user} {self.recipe} - shopping cart'


class ShortLink(models.Model):

    recipe = models.OneToOneField(
        Recipe,
        on_delete=models.CASCADE,
        related_name='short_link',
        verbose_name='Рецепт',
        unique=True
    )

    short_link = models.URLField(
        'Короткая ссылка',
        unique=True
    )

    class Meta:
        verbose_name = 'Короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'
        constraints = [
            models.UniqueConstraint(fields=['short_link', 'recipe'],
                                    name='unique_shortlink')
        ]

    def __str__(self):
        return f'{self.recipe} short link'
