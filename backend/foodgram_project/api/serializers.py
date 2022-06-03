from re import match

from django.contrib.auth import get_user_model, password_validation
from django.core import exceptions
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from foodgram_project.settings import PROJECT_SETTINGS
from ingredients.models import Ingredient, MeasurementUnit
from recipes.models import (Recipe, RecipeIngredientAmount, RecipeTag,
                            UserFavoriteRecipe, UserShoppingCart)
from tags.models import Tag
from users.models import SubscribeUser

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    '''
    Класс IngredientSerializer для модели Ingredient.
    '''
    measurement_unit = serializers.SlugRelatedField(
        slug_field='name',
        queryset=MeasurementUnit.objects.all(),
    )

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    '''
    Класс IngredientForRecipeSerializer.
    '''
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit.name'
    )

    class Meta:
        model = RecipeIngredientAmount
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class TagSerializer(serializers.ModelSerializer):
    '''
    Класс TagSerializer для модели Tag.
    '''
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class GetTokenSerializer(serializers.Serializer):
    '''
    Класс GetTokenSerializer для получения токена.
    '''
    email = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ('email', 'password',)


class UserCreateSerializer(serializers.ModelSerializer):
    '''
    Класс UserCreateSerializer для регистрации пользователя модели User.
    '''
    password = serializers.CharField(
        max_length=150,
        write_only=True,
    )
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def create(self, validated_data):
        user = super(UserCreateSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_password(self, value):
        try:
            password_validation.validate_password(value)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(list(e))
        return value

    def validate_username(self, value):
        pattern = PROJECT_SETTINGS.get(
            'users_validate_patter_username', r'^[\w.@+-]+\Z')
        if match(pattern, value):
            return value

        raise serializers.ValidationError(
            f"username must match pattern '{pattern}'"
        )


class UserSerializer(serializers.ModelSerializer):
    '''
    Класс UserSerializer для модели User.
    '''
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, user_obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user: User = request.user
            return (
                SubscribeUser.objects
                .filter(user=user, author=user_obj)
                .exists()
            )
        return False


class UserChangePasswordSerializer(serializers.Serializer):
    '''
    Класс UserChangePasswordSerializer для смены пароля модели User.
    '''
    current_password = serializers.CharField()
    new_password = serializers.CharField(max_length=150)

    def validate_current_password(self, value):
        user = self.context.get('user')
        if user.check_password(value):
            return value
        raise serializers.ValidationError(
            'does not match the current password'
        )

    def validate_new_password(self, value):
        try:
            password_validation.validate_password(value)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(list(e))
        return value


class ResipeSerializer(serializers.ModelSerializer):
    '''
    Класс ResipeSerializer для модели Recipe.
    '''
    tags = TagSerializer(required=True, many=True)
    author = UserSerializer()
    ingredients = IngredientForRecipeSerializer(
        source='recipeingredientamount_set',
        many=True
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        user = request.user
        return (user and user.is_authenticated
                and UserFavoriteRecipe.objects.filter(
                    user=user, recipe=obj
                ).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        user = request.user
        return (user and user.is_authenticated
                and UserShoppingCart.objects.filter(
                    user=user, recipe=obj
                ).exists())


class AmountSerialazer(serializers.Serializer):
    '''
    Класс AmountSerialazer.
    '''
    id = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField(required=True)

    def validate_amount(self, value):
        min_value = PROJECT_SETTINGS.get('ingredient_min_amount', 1)
        if value >= min_value:
            return value
        raise serializers.ValidationError(
            f'amount must be >= {min_value}!!'
        )


class ResipeEditSerializer(serializers.ModelSerializer):
    '''
    Класс ResipeEditSerializer.
    '''
    ingredients = AmountSerialazer(many=True, required=True)
    tags = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_cooking_time(self, value):
        min_value = PROJECT_SETTINGS.get('recipes_min_cooking_time', 1)
        if value >= min_value:
            return value
        raise serializers.ValidationError(
            f'cooking_time must be >= {min_value}!!'
        )

    def validate_ingredients(self, values):
        set_of_ingredients = set()
        for value in values:
            ingredient = value['id']
            if ingredient not in set_of_ingredients:
                set_of_ingredients.add(ingredient)
            else:
                raise serializers.ValidationError(
                    'Ingredients should not be repeated!'
                )
        return values

    def validate_tags(self, values):
        set_of_tags = set()
        for value in values:
            tag = value
            if tag not in set_of_tags:
                set_of_tags.add(tag)
            else:
                raise serializers.ValidationError(
                    'Tags should not be repeated!'
                )
        return values

    def validate(self, data):
        fields = self.Meta.fields
        err = []
        for field in fields:
            if field == 'image':
                continue
            if not data.get(field):
                err.append({field: 'This field is required'})
        if len(err) > 0:
            raise serializers.ValidationError(err)
        return data

    @transaction.atomic
    def create(self, validated_data):
        user = self.context.get('user')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe: Recipe = Recipe.objects.create(**validated_data, author=user)
        for tag in tags:
            recipe.tags.add(tag)
        for data_value in ingredients:
            ingredient = data_value['id']
            amount = data_value['amount']
            RecipeIngredientAmount.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount
            )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        recipe: Recipe = instance
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        for key, value in validated_data.items():
            setattr(recipe, key, value)
        recipe.save()

        RecipeTag.objects.filter(recipe=recipe).delete()
        for tag in tags:
            recipe.tags.add(tag)

        RecipeIngredientAmount.objects.filter(recipe=recipe).delete()
        for data_value in ingredients:
            ingredient = data_value['id']
            amount = data_value['amount']
            RecipeIngredientAmount.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount
            )
        return recipe


class ResipeShortListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        request = self.context.get('request', None)
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get('recipes_limit')

        try:
            recipes_limit = int(recipes_limit)
        except ValueError:
            recipes_limit = None
        except TypeError:
            recipes_limit = None

        iterable = data.all()[:recipes_limit]

        return [
            self.child.to_representation(item) for item in iterable
        ]


class ResipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        list_serializer_class = ResipeShortListSerializer


class UserSubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = ResipeShortSerializer(many=True)
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, user_obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user: User = request.user
            return (
                SubscribeUser.objects
                .filter(user=user, author=user_obj)
                .exists()
            )
        return False

    def get_recipes_count(self, user_obj):
        return user_obj.recipes.count()
