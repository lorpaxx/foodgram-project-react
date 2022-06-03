from django.contrib import admin
from recipes.models import (Recipe, RecipeIngredientAmount, RecipeTag,
                            UserFavoriteRecipe, UserShoppingCart)


class TagInline(admin.TabularInline):
    '''
    Класс TagInline.
    '''
    model = RecipeTag
    extra = 3


class IngredientInline(admin.TabularInline):
    '''
    Класс IngredientInline.
    '''
    model = RecipeIngredientAmount
    extra = 3


class RecipeAdmin(admin.ModelAdmin):
    '''
    Класс RecipeAdmin.
    '''
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
    list_editable = (
        'author',
        'name',
        'text',
        'cooking_time',
        'image',
    )
    list_filter = ('tags__name', )


class RecipeTagAdmin(admin.ModelAdmin):
    '''
    Класс RecipeTagAdmin.
    '''
    list_display = (
        'pk',
        'recipe',
        'tag',
    )
    list_editable = (
        'recipe',
        'tag',
    )
    list_filter = ('tag', )


class RecipeIngredientAmountAdmin(admin.ModelAdmin):
    '''
    RecipeIngredientAmountAdmin.
    '''
    list_display = (
        'pk',
        'recipe',
        'ingredient',
        'amount'
    )
    list_editable = (
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = (
        'recipe__name',
        'recipe__author__email',
        'recipe__author__username',
    )
    raw_id_fields = ('ingredient', 'recipe')


class UserFavoriteRecipeAdmin(admin.ModelAdmin):
    '''
    Класс UserFavoriteRecipeAdmin.
    '''
    list_display = (
        'pk',
        'user',
        'recipe',
    )
    list_editable = (
        'user',
        'recipe',
    )
    search_fields = (
        'recipe__name',
        'recipe__author__email',
        'recipe__author__username',
    )


class UserShoppingCartAdmin(admin.ModelAdmin):
    '''
    Класс UserShoppingCartAdmin.
    '''
    list_display = (
        'pk',
        'user',
        'recipe',
    )
    list_editable = (
        'user',
        'recipe',
    )
    search_fields = (
        'recipe__name',
        'recipe__author__email',
        'recipe__author__username',
    )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
admin.site.register(RecipeIngredientAmount, RecipeIngredientAmountAdmin)
admin.site.register(UserFavoriteRecipe, UserFavoriteRecipeAdmin)
admin.site.register(UserShoppingCart, UserShoppingCartAdmin)
