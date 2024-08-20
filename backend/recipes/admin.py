from django.contrib import admin

from .models import Ingredient, Favorite, Recipe, RecipeIngredient, Tag


class IngredientInline(admin.StackedInline):
    model = RecipeIngredient
    extra = 0


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_editable = ('measurement_unit',)
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    inlines = (
        IngredientInline,
    )
    list_display = (
        'name',
        'author',
        'is_favorited_count',
    )
    readonly_fields = ('is_favorited_count',)
    search_fields = (
        'name',
        'author__username',
    )
    list_filter = ('tags',)
    filter_horizontal = ('tags',)

    def is_favorited_count(self, obj):
        return obj.is_favorited.count()
    is_favorited_count.short_description = 'Добавления в избранное'


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)

    # list_display_links


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
