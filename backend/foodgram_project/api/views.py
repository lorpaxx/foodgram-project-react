from api.serializers import IngredientSerializer
from ingredients.models import Ingredient
from rest_framework import filters, mixins, viewsets


class IngredientViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    '''
    Класс IngredientViewSet для модели Ingredient.
    '''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
