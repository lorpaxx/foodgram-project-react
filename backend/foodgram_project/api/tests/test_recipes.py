import base64
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from ingredients.models import Ingredient, MeasurementUnit
from recipes.models import (Recipe, RecipeIngredientAmount, RecipeTag,
                            UserFavoriteRecipe, UserShoppingCart)
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase, override_settings
from tags.models import Tag

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


def add_num_to_value(d: dict, value: int):
    res = {}
    for key, val in d.items():
        res[key] = val + str(value)
    return res


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class RecipesTest(APITestCase):
    '''
    Тестируем модель /api/recipes/.
    '''
    @classmethod
    def setUpClass(cls):
        '''
        Создаём фикстуры.
        '''
        super().setUpClass()

        cls.url = '/api/recipes/'

        cls.USER_DATA = {
            'first_name': 'Тест',
            'last_name': 'Тестович',
            'email': 'test@test_domain.info',
            'username': 'usertest',
            'password': 'test_123',
        }
        cls.user1 = User.objects.create_user(
            **(add_num_to_value(cls.USER_DATA, 1)))
        cls.user2 = User.objects.create_user(
            **(add_num_to_value(cls.USER_DATA, 2)))
        cls.author = User.objects.create_user(
            **(add_num_to_value(cls.USER_DATA, 3)))
        cls.token1 = Token.objects.create(user=cls.user1)
        cls.token2 = Token.objects.create(user=cls.user2)
        cls.token_author = Token.objects.create(user=cls.author)

        cls.TAG_DATA = {
            'name': 'Tag',
            'slug': 'Tag',
            'color': '#11111',
        }
        cls.tag1 = Tag.objects.create(**(add_num_to_value(cls.TAG_DATA, 1)))
        cls.tag2 = Tag.objects.create(**(add_num_to_value(cls.TAG_DATA, 2)))
        cls.tag3 = Tag.objects.create(**(add_num_to_value(cls.TAG_DATA, 3)))

        cls.m_u = MeasurementUnit.objects.create(name='mu')

        cls.ingredient1 = Ingredient.objects.create(
            name='ingredient1', measurement_unit=cls.m_u)
        cls.ingredient2 = Ingredient.objects.create(
            name='ingredient1', measurement_unit=cls.m_u)
        cls.ingredient3 = Ingredient.objects.create(
            name='ingredient1', measurement_unit=cls.m_u)

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
        cls.small_gif_base64 = base64.b64encode(cls.small_gif)

        cls.recipe: Recipe = Recipe.objects.create(
            author=cls.author, name='Тест Рецепт', text='Много текста',
            cooking_time=42, image=cls.uploaded
        )
        cls.recipe_tag1 = RecipeTag.objects.create(
            recipe=cls.recipe, tag=cls.tag1)
        cls.recipe_tag2 = RecipeTag.objects.create(
            recipe=cls.recipe, tag=cls.tag2)
        cls.recipe_ingredient_amount1 = RecipeIngredientAmount.objects.create(
            recipe=cls.recipe, ingredient=cls.ingredient1, amount=1)
        cls.recipe_ingredient_amount2 = RecipeIngredientAmount.objects.create(
            recipe=cls.recipe, ingredient=cls.ingredient2, amount=2)
        cls.recipe_ingredient_amount3 = RecipeIngredientAmount.objects.create(
            recipe=cls.recipe, ingredient=cls.ingredient3, amount=5)

        cls.favorite_recipe = UserFavoriteRecipe.objects.create(
            user=cls.user2, recipe=cls.recipe)
        cls.shop_recipe = UserShoppingCart.objects.create(
            user=cls.user1, recipe=cls.recipe)

    @classmethod
    def tearDownClass(cls):
        '''
        Удаляем лишнее по завершении тестов.
        '''
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        '''
        Создадим клиенты для каждого теста.
        '''
        self.client = APIClient()

        self.auth_client1 = APIClient()
        self.auth_client1.credentials(
            HTTP_AUTHORIZATION='Token ' + RecipesTest.token1.key)

        self.auth_client2 = APIClient()
        self.auth_client2.credentials(
            HTTP_AUTHORIZATION='Token ' + RecipesTest.token2.key)

        self.author_client = APIClient()
        self.author_client.credentials(
            HTTP_AUTHORIZATION='Token ' + RecipesTest.token_author.key)

    def test_api_recipes_01_url_list_and_retrieve_ok(self):
        '''
        Тестируем доступность url.
        '''
        urls = [
            RecipesTest.url,
            RecipesTest.url + f'{RecipesTest.recipe.id}/',
        ]
        for url in urls:
            with self.subTest(url=url):
                resp = self.client.get(url)
                self.assertEqual(
                    resp.status_code, status.HTTP_200_OK,
                    'status code не совпадает с ожидаемым'
                )

    def test_api_recipes_02_url_test_retrieve(self):
        '''
        Тестируем ответ retrieve /api/recipes/{id}/.
        '''
        recipe: Recipe = RecipesTest.recipe

        url = RecipesTest.url + f'{recipe.id}/'
        resp = self.client.get(url)
        try:
            resp_data: dict = resp.json()
        except Exception as err:
            self.assertTrue(
                True,
                msg=f'responce data is not json: {err}'
            )
        self.assertIsInstance(resp_data, dict, 'В ответе не dict')

        fields_name = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]
        self.assertEqual(
            len(resp_data), len(fields_name),
            'В ответе число ключей отличается.'
        )
        for field in fields_name:
            with self.subTest(field=field):
                self.assertIn(
                    field, resp_data,
                    f'в ответе нет ключа {field}'
                )
        fields_name_value = {
            'id': recipe.pk,
            'is_favorited': False,
            'is_in_shopping_cart': False,
            'name': recipe.name,
            'text': recipe.text,
            'cooking_time': recipe.cooking_time
        }
        for field, value in fields_name_value.items():
            with self.subTest(field=field):
                self.assertEqual(
                    resp_data[field], value,
                    f'в ответе {field} не совпадает с ожидаемым.'
                )

        self.assertIsInstance(
            resp_data['tags'], list, 'В ключе tags не list')
        self.assertEqual(
            len(resp_data['tags']), recipe.tags.count(),
            'Число tags не совпадает с ожидаемым.'
        )

        self.assertIsInstance(
            resp_data['author'], dict, 'В ключе author не list')
        fields_name = {
            'id': RecipesTest.author.id,
            'email': RecipesTest.author.email,
            'first_name': RecipesTest.author.first_name,
            'last_name': RecipesTest.author.last_name,
            'username': RecipesTest.author.username,
            'is_subscribed': False,
        }
        self.assertEqual(
            len(resp_data['author']), len(fields_name),
            'В ответе d в ключе author число ключей отличается.'
        )
        for field in fields_name:
            with self.subTest(field=field):
                self.assertIn(
                    field, resp_data['author'],
                    f'В ответе в ключе author нет ключа {field}'
                )
        for field in fields_name:
            with self.subTest(field=field):
                self.assertEqual(
                    resp_data['author'][field], fields_name[field],
                    f'в ответе {field} не совпадает с ожидаемым.'
                )

        self.assertIsInstance(
            resp_data['ingredients'], list, 'В ключе ingredients не list')
        self.assertEqual(
            len(resp_data['ingredients']), recipe.ingredients.count())

        for ingredient in resp_data['ingredients']:
            fields_name = [
                'id',
                'name',
                'measurement_unit',
                'amount',
            ]
            for field in fields_name:
                with self.subTest(field=field):
                    self.assertIn(
                        field, ingredient,
                        f'В ответе в ключе нет ключа {field}'
                    )
            ingrid: Ingredient = Ingredient.objects.get(id=ingredient['id'])
            ingred_amount = RecipeIngredientAmount.objects.get(
                recipe=recipe, ingredient=ingrid)
            fields_name = {
                'id': ingrid.id,
                'name': ingrid.name,
                'measurement_unit': ingrid.measurement_unit.name,
                'amount': ingred_amount.amount,
            }
            for field in fields_name:
                with self.subTest(field=field):
                    self.assertEqual(
                        ingredient[field], fields_name[field],
                        f'в ответе {field} не совпадает с ожидаемым.'
                    )

    def test_api_recipes_03_url_test_list(self):
        '''
        Тестируем ответ retrieve /api/recipes/.
        '''
        url = RecipesTest.url
        resp = self.client.get(url)

        try:
            resp_data: dict = resp.json()
        except Exception as err:
            self.assertTrue(
                True,
                msg=f'responce data is not json: {err}'
            )
        self.assertIsInstance(
            resp_data, dict,
            'В ответе не dict'
        )
        fields_name = {
            'count': int,
            'next': (str, None),
            'previous': (str, None),
            'results': list,
        }
        self.assertEqual(
            len(resp_data), len(fields_name),
            'Число строк в ответе отличается.'
        )
        for field in fields_name:
            with self.subTest(field=field):
                self.assertIn(
                    field, fields_name,
                    f'В ответе нет поля {field}'
                )
        result = resp_data.get('results')
        self.assertIsInstance(
            result, list,
            'В ответе result не типа list'
        )
        self.assertEqual(
            len(result), Recipe.objects.count(),
            'В result неожиданное число рецептов'
        )

        resp_data = result[0]
        self.assertIsInstance(resp_data, dict, 'В ответе не dict')

        fields_name = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]
        self.assertEqual(
            len(resp_data), len(fields_name),
            'В ответе число ключей отличается.'
        )
        for field in fields_name:
            with self.subTest(field=field):
                self.assertIn(
                    field, resp_data,
                    f'в ответе нет ключа {field}'
                )

    def test_api_recipes_04_url_test_create_valid(self):
        '''
        Тестируем создание рецепта /api/recipes/.
        '''
        count_recipes = Recipe.objects.count()
        count_recipe_tags = RecipeTag.objects.count()
        count_recipe_ingred = RecipeIngredientAmount.objects.count()

        image_data = RecipesTest.small_gif_base64
        recipe_data = {
            'ingredients': [
                {'id': RecipesTest.ingredient1.id, 'amount': 1},
                {'id': RecipesTest.ingredient2.id, 'amount': 2},
                {'id': RecipesTest.ingredient3.id, 'amount': 3},
            ],
            'tags': [RecipesTest.tag1.id, RecipesTest.tag2.id],
            'image': image_data,
            'name': 'ТестРецепт1',
            'text': 'Текст ТестРецепта',
            'cooking_time': 5
        }
        url = RecipesTest.url
        resp = self.author_client.post(url, data=recipe_data, format='json')
        self.assertEqual(
            resp.status_code, status.HTTP_201_CREATED,
            'В ответе не ожидаемый status code'
        )

        try:
            resp_data: dict = resp.json()
        except Exception as err:
            self.assertTrue(
                True,
                msg=f'responce data is not json: {err}'
            )
        self.assertIsInstance(resp_data, dict, 'В ответе не dict')

        fields_name = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]
        self.assertEqual(
            len(resp_data), len(fields_name),
            'В ответе число ключей отличается.'
        )
        for field in fields_name:
            with self.subTest(field=field):
                self.assertIn(
                    field, resp_data,
                    f'в ответе нет ключа {field}'
                )

        self.assertEqual(
            Recipe.objects.count(), count_recipes + 1,
            'В базе новый Recipe не сохранился'
        )
        self.assertEqual(
            RecipeTag.objects.count(), count_recipe_tags + 2,
            'В базе новый RecipeTag не сохранился'
        )
        self.assertEqual(
            RecipeIngredientAmount.objects.count(), count_recipe_ingred + 3,
            'В базе новый RecipeIngredientAmount не сохранился'
        )

    def test_api_recipes_05_url_test_create_invalid(self):
        '''
        Тестируем несоздание рецепта /api/recipes/.
        '''
        image_data = RecipesTest.small_gif_base64
        recipe_data = {
            'ingredients': [
                {'id': RecipesTest.ingredient1.id, 'amount': 1},
                {'id': RecipesTest.ingredient2.id, 'amount': 2},
                {'id': RecipesTest.ingredient3.id, 'amount': 3},
            ],
            'tags': [RecipesTest.tag1.id, RecipesTest.tag2.id],
            'image': image_data,
            'name': 'ТестРецепт1',
            'text': 'Текст ТестРецепта',
            'cooking_time': 5
        }
        url = RecipesTest.url
        resp = self.client.post(url, data=recipe_data, format='json')
        self.assertEqual(
            resp.status_code, status.HTTP_401_UNAUTHORIZED,
            'В ответе не ожидаемый status code'
        )
        recipe_data = {
            'ingredients': [
                {'id': 10000, 'amount': 1},
            ],
            'tags': [RecipesTest.tag1.id, RecipesTest.tag2.id],
            'image': image_data,
            'name': 'ТестРецепт1',
            'text': 'Текст ТестРецепта',
            'cooking_time': 5
        }
        resp = self.auth_client1.post(url, data=recipe_data, format='json')
        self.assertEqual(
            resp.status_code, status.HTTP_400_BAD_REQUEST,
            'В ответе не ожидаемый status code'
        )
        self.assertIn('ingredients', resp.json())

        recipe_data = {
            'ingredients': [
                {'id': 1, 'amount': 1},
            ],
            'tags': [4, 2],
            'image': image_data,
            'name': 'ТестРецепт1',
            'text': 'Текст ТестРецепта',
            'cooking_time': 5
        }
        resp = self.auth_client1.post(url, data=recipe_data, format='json')
        self.assertEqual(
            resp.status_code, status.HTTP_400_BAD_REQUEST,
            'В ответе не ожидаемый status code'
        )
        self.assertIn('tags', resp.json())

        recipe_data = {
            'ingredients': [
                {'id': 1, 'amount': 1},
            ],
            'tags': [1, 2],
            'image': 'vfbvfbvjfb',
            'name': 'ТестРецепт1',
            'text': 'Текст ТестРецепта',
            'cooking_time': 5
        }
        resp = self.auth_client1.post(url, data=recipe_data, format='json')
        self.assertEqual(
            resp.status_code, status.HTTP_400_BAD_REQUEST,
            'В ответе не ожидаемый status code'
        )
        self.assertIn('image', resp.json())

        recipe_data = {
            'ingredients': [
                {'id': 1, 'amount': 1},
            ],
            'tags': [1, 2],
            'image': image_data,
            'name': 'a' * 201,
            'text': 'Текст ТестРецепта',
            'cooking_time': 5
        }
        resp = self.auth_client1.post(url, data=recipe_data, format='json')
        self.assertEqual(
            resp.status_code, status.HTTP_400_BAD_REQUEST,
            'В ответе не ожидаемый status code'
        )
        self.assertIn('name', resp.json())

        recipe_data = {
            'ingredients': [
                {'id': 1, 'amount': 1},
            ],
            'tags': [1, 2],
            'image': image_data,
            'name': 'a' * 201,
            'cooking_time': 5
        }
        resp = self.auth_client1.post(url, data=recipe_data, format='json')
        self.assertEqual(
            resp.status_code, status.HTTP_400_BAD_REQUEST,
            'В ответе не ожидаемый status code'
        )
        self.assertIn('name', resp.json())

        recipe_data = {
            'ingredients': [
                {'id': 1, 'amount': 1},
            ],
            'tags': [1, 2],
            'image': image_data,
            'name': 'a' * 200,
            'text': 'Текст ТестРецепта',
            'cooking_time': 0
        }
        resp = self.auth_client1.post(url, data=recipe_data, format='json')
        self.assertEqual(
            resp.status_code, status.HTTP_400_BAD_REQUEST,
            'В ответе не ожидаемый status code'
        )
        self.assertIn('cooking_time', resp.json())

    # def test_api_recipes_06_url_test_patch(self):
    #     '''
    #     Тестируем изменение рецепта.
    #     '''
    #     image_data = RecipesTest.small_gif_base64
    #     recipe: Recipe = RecipesTest.recipe
    #     url = RecipesTest.url + f'{recipe.id}/'
    #     recipe_data = {
    #         'ingredients': [
    #             {'id': RecipesTest.ingredient1.id, 'amount': 1},
    #             {'id': RecipesTest.ingredient2.id, 'amount': 2},
    #             {'id': RecipesTest.ingredient3.id, 'amount': 3},
    #         ],
    #         'tags': [RecipesTest.tag1.id, RecipesTest.tag2.id],
    #         'image': image_data,
    #         'name': 'ТестРецепт1',
    #         'text': 'Текст ТестРецепта',
    #         'cooking_time': 5
    #     }
    #     resp = self.client.patch(url, data=recipe_data, format='json')
    #     self.assertEqual(
    #         resp.status_code, status.HTTP_401_UNAUTHORIZED,
    #         'В ответе не ожидаемый status code'
    #     )
    #     resp = self.auth_client1.patch(url, data=recipe_data, format='json')
    #     self.assertEqual(
    #         resp.status_code, status.HTTP_403_FORBIDDEN,
    #         'В ответе не ожидаемый status code'
    #     )
    #     recipe_data = {
    #         'tags': [RecipesTest.tag1.id, RecipesTest.tag2.id],
    #         'image': image_data,
    #         'name': 'ТестРецепт1',
    #         'text': 'Текст ТестРецепта',
    #         'cooking_time': 5
    #     }
    #     resp = self.author_client.patch(url, data=recipe_data, format='json')
    #     self.assertEqual(
    #         resp.status_code, status.HTTP_400_BAD_REQUEST,
    #         'В ответе не ожидаемый status code'
    #     )
    #     self.assertIn('ingredients', resp.json())

    #     recipe_data = {
    #         'ingredients': [
    #             {'id': RecipesTest.ingredient1.id, 'amount': 0},
    #             {'id': RecipesTest.ingredient2.id, 'amount': 2},
    #             {'id': RecipesTest.ingredient3.id, 'amount': 3},
    #         ],
    #         'tags': [RecipesTest.tag1.id, RecipesTest.tag2.id],
    #         'image': image_data,
    #         'name': 'ТестРецепт1',
    #         'text': 'Текст ТестРецепта',
    #         'cooking_time': 5
    #     }
    #     resp = self.author_client.patch(url, data=recipe_data, format='json')
    #     self.assertEqual(
    #         resp.status_code, status.HTTP_400_BAD_REQUEST,
    #         'В ответе не ожидаемый status code'
    #     )
    #     self.assertIn('ingredients', resp.json())

    #     recipe_data = {
    #         'ingredients': [
    #             {'id': RecipesTest.ingredient1.id, 'amount': 1},
    #             {'id': RecipesTest.ingredient2.id, 'amount': 2},
    #             {'id': RecipesTest.ingredient3.id, 'amount': 3},
    #         ],
    #         # 'tags': [RecipesTest.tag1.id, RecipesTest.tag2.id],
    #         'image': image_data,
    #         'name': 'ТестРецепт1',
    #         'text': 'Текст ТестРецепта',
    #         'cooking_time': 5
    #     }
    #     resp = self.author_client.patch(url, data=recipe_data, format='json')
    #     self.assertEqual(
    #         resp.status_code, status.HTTP_400_BAD_REQUEST,
    #         'В ответе не ожидаемый status code'
    #     )
    #     self.assertIn('tags', resp.json())

    #     recipe_data = {
    #         'ingredients': [
    #             {'id': RecipesTest.ingredient1.id, 'amount': 1},
    #             {'id': RecipesTest.ingredient2.id, 'amount': 2},
    #             {'id': RecipesTest.ingredient3.id, 'amount': 3},
    #         ],
    #         'tags': [RecipesTest.tag1.id, RecipesTest.tag2.id],
    #         # 'image': image_data,
    #         'name': 'ТестРецепт1',
    #         'text': 'Текст ТестРецепта',
    #         'cooking_time': 5
    #     }
    #     resp = self.author_client.patch(url, data=recipe_data, format='json')
    #     self.assertEqual(
    #         resp.status_code, status.HTTP_400_BAD_REQUEST,
    #         'В ответе не ожидаемый status code'
    #     )
    #     self.assertIn('image', resp.json())

    #     recipe_data = {
    #         'ingredients': [
    #             {'id': RecipesTest.ingredient1.id, 'amount': 1},
    #             {'id': RecipesTest.ingredient2.id, 'amount': 2},
    #             {'id': RecipesTest.ingredient3.id, 'amount': 3},
    #         ],
    #         'tags': [RecipesTest.tag1.id, RecipesTest.tag2.id],
    #         'image': image_data,
    #         # 'name': 'ТестРецепт1',
    #         'text': 'Текст ТестРецепта',
    #         'cooking_time': 5
    #     }
    #     resp = self.author_client.patch(url, data=recipe_data, format='json')
    #     self.assertEqual(
    #         resp.status_code, status.HTTP_400_BAD_REQUEST,
    #         'В ответе не ожидаемый status code'
    #     )
    #     self.assertIn('name', resp.json())

    #     recipe_data = {
    #         'ingredients': [
    #             {'id': RecipesTest.ingredient1.id, 'amount': 1},
    #             {'id': RecipesTest.ingredient2.id, 'amount': 2},
    #             {'id': RecipesTest.ingredient3.id, 'amount': 3},
    #         ],
    #         'tags': [RecipesTest.tag1.id, RecipesTest.tag2.id],
    #         'image': image_data,
    #         'name': 'ТестРецепт1',
    #         # 'text': 'Текст ТестРецепта',
    #         'cooking_time': 5
    #     }
    #     resp = self.author_client.patch(url, data=recipe_data, format='json')
    #     self.assertEqual(
    #         resp.status_code, status.HTTP_400_BAD_REQUEST,
    #         'В ответе не ожидаемый status code'
    #     )
    #     self.assertIn('text', resp.json())

    #     recipe_data = {
    #         'ingredients': [
    #             {'id': RecipesTest.ingredient1.id, 'amount': 1},
    #             {'id': RecipesTest.ingredient2.id, 'amount': 2},
    #             {'id': RecipesTest.ingredient3.id, 'amount': 3},
    #         ],
    #         'tags': [RecipesTest.tag1.id, RecipesTest.tag2.id],
    #         'image': image_data,
    #         'name': 'ТестРецепт1',
    #         'text': 'Текст ТестРецепта',
    #         'cooking_time': 0
    #     }
    #     resp = self.author_client.patch(url, data=recipe_data, format='json')
    #     self.assertEqual(
    #         resp.status_code, status.HTTP_400_BAD_REQUEST,
    #         'В ответе не ожидаемый status code'
    #     )
    #     self.assertIn('cooking_time', resp.json())

    #     recipe_data = {
    #         'ingredients': [
    #             {'id': RecipesTest.ingredient1.id, 'amount': 1},
    #             {'id': RecipesTest.ingredient2.id, 'amount': 2},
    #             {'id': RecipesTest.ingredient3.id, 'amount': 3},
    #         ],
    #         'tags': [RecipesTest.tag1.id, RecipesTest.tag2.id],
    #         'image': image_data,
    #         'name': 'ТестРецепт1',
    #         'text': 'Текст ТестРецепта',
    #         'cooking_time': 1
    #     }
    #     resp = self.author_client.patch(
    #         RecipesTest.url + '1000/', data=recipe_data, format='json')
    #     self.assertEqual(
    #         resp.status_code, status.HTTP_404_NOT_FOUND,
    #         'В ответе не ожидаемый status code'
    #     )

    #     recipe_data = {
    #         'ingredients': [
    #             {'id': RecipesTest.ingredient1.id, 'amount': 5}
    #         ],
    #         'tags': [RecipesTest.tag3.id],
    #         'image': image_data,
    #         'name': 'ТестРецепт15',
    #         'text': 'Текст ТестРецепта16',
    #         'cooking_time': 15
    #     }
    #     url = RecipesTest.url + f'{recipe.pk}/'
    #     resp = self.author_client.patch(url, data=recipe_data, format='json')
    #     self.assertEqual(
    #         resp.status_code, status.HTTP_200_OK,
    #         'В ответе не ожидаемый status code'
    #     )
    #     try:
    #         resp_data: dict = resp.json()
    #     except Exception as err:
    #         self.assertTrue(
    #             True,
    #             msg=f'responce data is not json: {err}'
    #         )
    #     self.assertIsInstance(resp_data, dict, 'В ответе не dict')

    #     fields_name = [
    #         'id',
    #         'tags',
    #         'author',
    #         'ingredients',
    #         'is_favorited',
    #         'is_in_shopping_cart',
    #         'name',
    #         'image',
    #         'text',
    #         'cooking_time'
    #     ]
    #     self.assertEqual(
    #         len(resp_data), len(fields_name),
    #         'В ответе число ключей отличается.'
    #     )
    #     for field in fields_name:
    #         with self.subTest(field=field):
    #             self.assertIn(
    #                 field, resp_data,
    #                 f'в ответе нет ключа {field}'
    #             )
    #     self.assertEqual(RecipeIngredientAmount.objects.count(), 1)
    #     self.assertEqual(RecipeTag.objects.count(), 1)

    def test_api_recipes_06_url_test_delete(self):
        '''
        Тестируем удаление рецептов.
        '''
        recipe: Recipe = RecipesTest.recipe
        count_recipes = Recipe.objects.count()
        url = RecipesTest.url + '1000/'

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        resp = self.auth_client1.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Recipe.objects.count(), count_recipes)

        url = RecipesTest.url + f'{recipe.pk}/'
        resp = self.auth_client1.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Recipe.objects.count(), count_recipes)

        resp = self.author_client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Recipe.objects.count(), count_recipes - 1)
