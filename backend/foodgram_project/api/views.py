from api.paginators import PageNumberCustomPaginator
from api.permissions import AuthorOrReadOnly
from api.serializers import (GetTokenSerializer, IngredientSerializer,
                             ResipeEditSerializer, ResipeSerializer,
                             ResipeShortSerializer, TagSerializer,
                             UserChangePasswordSerializer,
                             UserCreateSerializer, UserSerializer)
from django.contrib.auth import get_user_model
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from ingredients.models import Ingredient
from recipes.models import (Recipe, RecipeIngredientAmount, UserFavoriteRecipe,
                            UserShoppingCart)
from rest_framework import (decorators, filters, mixins, permissions, status,
                            viewsets)
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from tags.models import Tag

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
        token = Token.objects.get(user=user)
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
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    Класс TagViewSet для модели Tag.
    '''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


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


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = ResipeSerializer
    permission_classes = (AuthorOrReadOnly,)

    def create(self, request, *args, **kwargs):
        serializer = ResipeEditSerializer(
            data=request.data,
            context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output_serializer = ResipeSerializer(serializer.instance)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = ResipeEditSerializer(
            instance, data=request.data, partial=partial
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
        user = request.user
        recipe_id = kwargs.get('pk', 0)
        if not Recipe.objects.filter(id=recipe_id).exists():
            return Response(
                {'errors': f'recipe with id={recipe_id} does not exists'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        recipe = Recipe.objects.get(id=recipe_id)

        if request.method == 'POST':
            row, created = UserFavoriteRecipe.objects.get_or_create(
                recipe=recipe, user=user
            )
            if created:
                serializer = ResipeShortSerializer(instance=recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'the recipe is already in favorites'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if UserFavoriteRecipe.objects.filter(
            user=user, recipe=recipe
        ).exists():
            obj = UserFavoriteRecipe.objects.get(user=user, recipe=recipe)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': 'the recipe is not in favorites'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @decorators.action(
        methods=('post', 'delete',),
        permission_classes=(permissions.IsAuthenticated,),
        detail=True,
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def manager_sopping_cart(self, request, *args, **kwargs):
        user = request.user
        recipe_id = kwargs.get('pk', 0)
        if not Recipe.objects.filter(id=recipe_id).exists():
            return Response(
                {'errors': f'recipe with id={recipe_id} does not exists'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        recipe = Recipe.objects.get(id=recipe_id)

        if request.method == 'POST':
            row, created = UserShoppingCart.objects.get_or_create(
                recipe=recipe, user=user
            )
            if created:
                serializer = ResipeShortSerializer(instance=recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'the recipe is already in shopping cart'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if UserShoppingCart.objects.filter(
            user=user, recipe=recipe
        ).exists():
            obj = UserShoppingCart.objects.get(user=user, recipe=recipe)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': 'the recipe is not in shopping cart'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @decorators.action(
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,),
        detail=False,
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        print(request.query_params)
        user = request.user
        cart = (RecipeIngredientAmount.objects.filter(
            recipe__in_shopping__user=user).
            values(
                'ingredient__name',
                'ingredient__measurement_unit__name'
            ).annotate(total=models.Sum('amount')))
        with open(f'media/{user.username}.csv', 'w', encoding='utf-8') as f:
            from csv import writer
            csv_writer = writer(
                f, delimiter=';', quotechar='"', lineterminator='\n'
            )
            head_row = ['ingredient', 'measurement_unit', 'total']
            csv_writer.writerow(head_row)
            for row in cart:
                csv_writer.writerow(
                    [
                        row["ingredient__name"],
                        row["ingredient__measurement_unit__name"],
                        row["total"]
                    ]
                )
        with open(f'media/{user.username}.csv', 'r', encoding='utf-8') as f:
            file_data = f.read()

        response = HttpResponse(file_data, content_type='application/csv')
        response['Content-Disposition'] = (
            f'attachment; filename="{user.username}.csv"'
        )
        return response
