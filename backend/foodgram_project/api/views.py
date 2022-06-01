from csv import writer

from api.filters import IngredientFilter, RecipeFilter
from api.paginators import PageNumberCustomPaginator
from api.permissions import AuthorOrReadOnly
from api.serializers import (GetTokenSerializer, IngredientSerializer,
                             ResipeEditSerializer, ResipeSerializer,
                             ResipeShortSerializer, TagSerializer,
                             UserChangePasswordSerializer,
                             UserCreateSerializer, UserSerializer,
                             UserSubscribeSerializer)
from api.views_side_func import manage_many_to_many_model_with_user
from django.contrib.auth import get_user_model
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from ingredients.models import Ingredient
from recipes.models import (Recipe, RecipeIngredientAmount, UserFavoriteRecipe,
                            UserShoppingCart)
from rest_framework import decorators, mixins, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from tags.models import Tag
from users.models import SubscribeUser

User = get_user_model()


@decorators.api_view(('POST',))
def get_token(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email')
    password = serializer.validated_data.get('password')
    user = get_object_or_404(User, email=email)
    if (user.check_password(password)):
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'auth_token': token.key},
            status=status.HTTP_201_CREATED
        )
    return Response(status=status.HTTP_401_UNAUTHORIZED)


@decorators.api_view(('POST',))
def drop_token(request):
    user: User = request.user
    if user.is_authenticated:
        token = get_object_or_404(Token, user=user)
        token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        {'detail': 'Учетные данные не были предоставлены.'},
        status=status.HTTP_401_UNAUTHORIZED,
    )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    Класс IngredientViewSet для модели Ingredient.
    '''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    Класс TagViewSet для модели Tag.
    '''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class UserViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberCustomPaginator

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @decorators.action(
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,),
        detail=False,
        url_path='me',
        url_name='me'
    )
    def me(self, request, *args, **kwargs):
        user = self.request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @decorators.action(
        methods=('post',),
        permission_classes=(permissions.IsAuthenticated,),
        detail=False,
        url_path='set_password',
        url_name='set_password'
    )
    def set_new_password(self, request, *args, **kwargs):
        user = self.request.user
        serializer = UserChangePasswordSerializer(
            data=request.data,
            context={'user': user}
        )
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data.get('new_password'))
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,),
        detail=True,
        url_path='subscribe',
        url_name='subscribe'
    )
    def manage_subscribe(self, request, *args, **kwargs):
        return manage_many_to_many_model_with_user(
            request, *args, **kwargs,
            second_model=User,
            second_model_name='author',
            serializer_class=UserSubscribeSerializer,
            many_to_many_model=SubscribeUser
        )

    @decorators.action(
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,),
        detail=False,
        url_path='subscriptions',
        url_name='subscriptions'
    )
    def subscriptions(self, request, *args, **kwargs):
        user = request.user
        queryset = User.objects.filter(subscribe__user=user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSubscribeSerializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = UserSubscribeSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = ResipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = RecipeFilter
    pagination_class = PageNumberCustomPaginator

    def create(self, request, *args, **kwargs):
        serializer = ResipeEditSerializer(
            data=request.data,
            context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output_serializer = ResipeSerializer(
            serializer.instance, context={'request': request})
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ResipeEditSerializer(
            instance, data=request.data, partial=False
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        output_serializer = ResipeSerializer(serializer.instance)
        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,)

    @decorators.action(
        methods=('post', 'delete',),
        permission_classes=(permissions.IsAuthenticated,),
        detail=True,
        url_path='favorite',
        url_name='favorite',
    )
    def manage_favorite(self, request, *args, **kwargs):
        return manage_many_to_many_model_with_user(
            request, *args, **kwargs,
            second_model=Recipe,
            second_model_name='recipe',
            serializer_class=ResipeShortSerializer,
            many_to_many_model=UserFavoriteRecipe,
        )

    @decorators.action(
        methods=('post', 'delete',),
        permission_classes=(permissions.IsAuthenticated,),
        detail=True,
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def manager_sopping_cart(self, request, *args, **kwargs):
        return manage_many_to_many_model_with_user(
            request, *args, **kwargs,
            second_model=Recipe,
            second_model_name='recipe',
            serializer_class=ResipeShortSerializer,
            many_to_many_model=UserShoppingCart
        )

    @decorators.action(
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,),
        detail=False,
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request, *args, **kwargs):

        user: User = request.user

        cart = (
            RecipeIngredientAmount.objects.filter(
                recipe__in_shopping__user=user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit__name'
            ).annotate(total=models.Sum('amount'))
        )
        response = HttpResponse(content_type='text/csv')
        csv_writer = writer(
                response, delimiter=';', quotechar='"', lineterminator='\n'
            )
        csv_headers = ('Ингредиент', 'Размерность', 'Количество')
        csv_writer.writerow(csv_headers)
        for row in cart:
            csv_writer.writerow(
                [
                    row['ingredient__name'],
                    row['ingredient__measurement_unit__name'],
                    row['total']
                ]
            )
        response['Content-Disposition'] = (
            f'attachment;filename="{user.username}.csv"'
        )
        return response
