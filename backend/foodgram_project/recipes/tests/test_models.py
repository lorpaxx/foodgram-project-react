import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from ingredients.models import Ingredient, MeasurementUnit
from recipes.models import (Recipe, RecipeIngredientAmount, RecipeTag,
                            UserFavoriteRecipe, UserShoppingCart)
from tags.models import Tag
from users.models import User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class RecipeModelsTest(TestCase):
    '''
    Тестируем модель Recipe.
    '''
    @classmethod
    def setUpClass(cls):
        '''
        Создаём фикстуры.
        '''
        super().setUpClass()
        cls.USER_DATA = {
            'first_name': 'Тест',
            'last_name': 'Тестович',
            'email': 'test@test_domain.info',
            'username': 'usertest',
            'password': 'test_123',
        }

        cls.user: User = User.objects.create_user(**cls.USER_DATA)
        cls.tag: Tag = Tag.objects.create(
            name='Tag1',
            slug='Tag_1',
            color='#111111',
        )
        cls.m_u = MeasurementUnit.objects.create(name='Mu1')
        cls.ingrid = Ingredient.objects.create(
            name='ingrid_1', measurement_unit=cls.m_u)
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.recipe: Recipe = Recipe.objects.create(
            author=cls.user, name='Тест Рецепт', text='Много текста',
            cooking_time=42, image=cls.uploaded
        )
        cls.recipe_tag = RecipeTag.objects.create(
            recipe=cls.recipe, tag=cls.tag
        )
        cls.recipe_ingredient_amount = RecipeIngredientAmount.objects.create(
            recipe=cls.recipe, ingredient=cls.ingrid, amount=37
        )
        cls.favorite_recipe = UserFavoriteRecipe.objects.create(
            user=cls.user, recipe=cls.recipe
        )
        cls.shop_recipe = UserShoppingCart.objects.create(
            user=cls.user, recipe=cls.recipe
        )

    @classmethod
    def tearDownClass(cls):
        '''
        Удаляем лишнее по завершении тестов.
        '''
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_recipes_models_recipe_have_correct_verbose_name(self):
        '''
        Пробежимся по полям модели Recipe и проверим verbose_name.
        '''
        field_verboses = {
            'author': 'Автор',
            'name': 'Название',
            'text': 'Описание',
            'cooking_time': 'Время приготовления (в минутах)',
            'tags': 'Тег',
            'ingredients': 'Список ингредиентов'
        }
        recipe: Recipe = RecipeModelsTest.recipe
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    recipe._meta.get_field(field).verbose_name,
                    expected_value, (
                        'Тест не пройден, '
                        f'{recipe._meta.get_field(field).verbose_name} '
                        f'вместо {expected_value}'
                    )
                )

    def test_recipes_models_recipe_have_correct_help_text(self):
        '''
        Пробежимся по полям модели User и проверим help_text.
        '''
        field_help_text = {
            'author': 'Автор',
            'name': 'Название',
            'text': 'Описание',
            'cooking_time': 'Время приготовления (в минутах)',
            'tags': 'Тег',
            'ingredients': 'Список ингредиентов'
        }
        recipe: Recipe = RecipeModelsTest.recipe
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    recipe._meta.get_field(field).help_text,
                    expected_value,
                    (
                        'Тест не пройден, '
                        f'{recipe._meta.get_field(field).help_text} '
                        f'вместо {expected_value}'
                    )
                )

    def test_recipes_models_recipe_have_correct_max_length(self):
        '''
        Пробежимся по полям модели User и проверим max_length.
        '''
        field_max_length = {
            'name': 200,
        }
        recipe: Recipe = RecipeModelsTest.recipe
        for field, expected_value in field_max_length.items():
            with self.subTest(field=field):
                self.assertEqual(
                    recipe._meta.get_field(field).max_length,
                    expected_value,
                    (
                        'Тест не пройден, '
                        f'{recipe._meta.get_field(field).max_length} '
                        f'вместо {expected_value}'
                    )
                )

    def test_recipes_models_recipetags_have_correct_fields(self):
        '''
        Пробежимся по полям модели RecipeTag и проверим поля.
        '''
        recipe_tag: RecipeTag = RecipeModelsTest.recipe_tag

        field_verboses = {
            'recipe': 'Рецепт',
            'tag': 'Тег',
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    recipe_tag._meta.get_field(field).verbose_name,
                    expected_value, (
                        'Некореектный verbose_name, '
                        f'{recipe_tag._meta.get_field(field).verbose_name} '
                        f'вместо {expected_value}'
                    )
                )

        field_help_text = {
            'recipe': 'Рецепт',
            'tag': 'Тег',
        }

        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    recipe_tag._meta.get_field(field).help_text,
                    expected_value,
                    (
                        'Некореектный help_text, '
                        f'{recipe_tag._meta.get_field(field).help_text} '
                        f'вместо {expected_value}'
                    )
                )

    def test_recipes_models_recipeingredientsamount_have_correct_fields(self):
        '''
        Пробежимся по полям модели RecipeIngredientAmount и проверим поля.
        '''
        recipe_ingrid: RecipeIngredientAmount = (
            RecipeModelsTest.recipe_ingredient_amount)

        field_verboses = {
            'recipe': 'Рецепт',
            'ingredient': 'Ингридиент',
            'amount': 'Количество',
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    recipe_ingrid._meta.get_field(field).verbose_name,
                    expected_value, (
                        'Некореектный verbose_name, '
                        f'{recipe_ingrid._meta.get_field(field).verbose_name} '
                        f'вместо {expected_value}'
                    )
                )

        field_help_text = {
            'recipe': 'Рецепт',
            'ingredient': 'Ингридиент',
            'amount': 'Количество',
        }

        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    recipe_ingrid._meta.get_field(field).help_text,
                    expected_value,
                    (
                        'Некореектный help_text, '
                        f'{recipe_ingrid._meta.get_field(field).help_text} '
                        f'вместо {expected_value}'
                    )
                )

    def test_recipes_models_userfavoriterecipe_have_correct_fields(self):
        '''
        Пробежимся по полям модели RecipeIngredientAmount и проверим поля.
        '''
        favor_recipe: UserFavoriteRecipe = RecipeModelsTest.favorite_recipe

        field_verboses = {
            'recipe': 'Рецепт',
            'user': 'Пользователь',
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    favor_recipe._meta.get_field(field).verbose_name,
                    expected_value, (
                        'Некореектный verbose_name, '
                        f'{favor_recipe._meta.get_field(field).verbose_name} '
                        f'вместо {expected_value}'
                    )
                )

        field_help_text = {
            'recipe': 'Рецепт',
            'user': 'Пользователь',
        }

        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    favor_recipe._meta.get_field(field).help_text,
                    expected_value,
                    (
                        'Некореектный help_text, '
                        f'{favor_recipe._meta.get_field(field).help_text} '
                        f'вместо {expected_value}'
                    )
                )

    def test_recipes_models_usershoppingcart_have_correct_fields(self):
        '''
        Пробежимся по полям модели RecipeIngredientAmount и проверим поля.
        '''
        shop_recipe: UserShoppingCart = RecipeModelsTest.shop_recipe

        field_verboses = {
            'recipe': 'Рецепт',
            'user': 'Пользователь',
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    shop_recipe._meta.get_field(field).verbose_name,
                    expected_value, (
                        'Некореектный verbose_name, '
                        f'{shop_recipe._meta.get_field(field).verbose_name} '
                        f'вместо {expected_value}'
                    )
                )

        field_help_text = {
            'recipe': 'Рецепт',
            'user': 'Пользователь',
        }

        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    shop_recipe._meta.get_field(field).help_text,
                    expected_value,
                    (
                        'Некореектный help_text, '
                        f'{shop_recipe._meta.get_field(field).help_text} '
                        f'вместо {expected_value}'
                    )
                )
