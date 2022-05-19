from re import match

from django.contrib.auth import get_user_model, password_validation
from django.core import exceptions
from ingredients.models import Ingredient, MeasurementUnit
from rest_framework import serializers
from tags.models import Tag

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
    email = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ('email', 'password',)


class UserCreateSerializer(serializers.ModelSerializer):
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
        pattern = r'^[\w.@+-]+\Z'
        if match(pattern, value):
            return value

        raise serializers.ValidationError(
            f"username must match pattern '{pattern}'"
        )


class UserSerializer(serializers.ModelSerializer):
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
            return True
        return False


class UserChangePasswordSerializer(serializers.Serializer):
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
