from django_filters import FilterSet, rest_framework
from tags.models import Tag


class IngredientFilter(FilterSet):
    '''
    Класс IngredientFilter.
    '''
    name = rest_framework.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )


class RecipeFilter(FilterSet):
    '''
    Класс RecipeFilter.
    '''
    author = rest_framework.CharFilter(
        field_name='author__id',
    )
    is_favorited = rest_framework.CharFilter(method='get_favorited_filter')

    is_in_shopping_cart = rest_framework.CharFilter(
        method='get_in_shopping_cart_filter'
    )

    tags = rest_framework.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )

    def get_favorited_filter(self, queryset, name, value):
        '''
        Возвращает отфильтрованный queryset модели Recipe,
        элементы которых есть в UserFavoriteRecipe.
        '''
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated:
            if value == '1':
                return queryset.filter(in_favorite__user=user)
            elif value == '0':
                return queryset.exclude(in_favorite__user=user)
        return queryset

    def get_in_shopping_cart_filter(self, queryset, name, value):
        '''
        Возвращает отфильтрованный queryset модели Recipe,
        элементы которых есть в UserShoppingCart.
        '''
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated:
            if value == '1':
                return queryset.filter(in_shopping__user=user)
            elif value == '0':
                return queryset.exclude(in_shopping__user=user)
        return queryset
