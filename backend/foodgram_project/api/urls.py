from api.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                       UserViewSet, drop_token, get_token)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register('users', UserViewSet)
router.register('recipes', RecipeViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/login/', get_token, name='GetToken'),
    path('auth/token/logout/', drop_token, name='DropToken'),
]
