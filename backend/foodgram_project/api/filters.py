from django_filters import FilterSet, rest_framework
from ingredients.models import Ingredient


class IngredientFilter(FilterSet):

    name = rest_framework.CharFilter(
        field_name='name',
        lookup_expr='startswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)