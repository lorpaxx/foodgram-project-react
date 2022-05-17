from api.serializers import IngredientSerializer, TagSerializer
from ingredients.models import Ingredient
from rest_framework import filters, mixins, viewsets
from tags.models import Tag


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


class TagViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    '''
    Класс TagViewSet для модели Tag.
    '''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
