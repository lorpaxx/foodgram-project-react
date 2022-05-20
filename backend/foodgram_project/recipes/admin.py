from django.contrib import admin
from recipes.models import Recipe, RecipeIngredientAmount, RecipeTag


class TagInline(admin.TabularInline):
    model = RecipeTag
    extra = 3


class IngredientInline(admin.TabularInline):
    model = RecipeIngredientAmount
    extra = 3


class RecipeAdmin(admin.ModelAdmin):
    inlines = (
        TagInline,
        IngredientInline,
    )
    list_display = (
        'pk',
        'author',
        'name',
        'text',
        'cooking_time',
        'image',
    )


admin.site.register(Recipe, RecipeAdmin)
