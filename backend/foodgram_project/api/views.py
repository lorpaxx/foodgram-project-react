from api.paginators import PageNumberCustomPaginator
from api.serializers import (GetTokenSerializer, IngredientSerializer,
                             ResipeSerializer, TagSerializer,
                             UserChangePasswordSerializer,
                             UserCreateSerializer, UserSerializer)
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ingredients.models import Ingredient
from recipes.models import Recipe
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
    print(user)
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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
