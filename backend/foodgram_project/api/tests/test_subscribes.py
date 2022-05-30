import base64
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from ingredients.models import Ingredient, MeasurementUnit
from recipes.models import Recipe, RecipeIngredientAmount, RecipeTag
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase, override_settings
from tags.models import Tag
from users.models import SubscribeUser

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


def add_num_to_value(d: dict, value: int):
    res = {}
    for key, val in d.items():
        res[key] = val + str(value)
    return res


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class SubscribesTest(APITestCase):
    '''
    Тестируем модель /api/users/{id}/subscribe/.
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
            name='ingredient2', measurement_unit=cls.m_u)
        cls.ingredient3 = Ingredient.objects.create(
            name='ingredient3', measurement_unit=cls.m_u)

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
        RecipeTag.objects.create(
            recipe=cls.recipe, tag=cls.tag1)
        RecipeTag.objects.create(
            recipe=cls.recipe, tag=cls.tag2)
        RecipeTag.objects.create(
            recipe=cls.recipe, tag=cls.tag3)
        RecipeIngredientAmount.objects.create(
            recipe=cls.recipe, ingredient=cls.ingredient1, amount=1)
        RecipeIngredientAmount.objects.create(
            recipe=cls.recipe, ingredient=cls.ingredient2, amount=2)
        RecipeIngredientAmount.objects.create(
            recipe=cls.recipe, ingredient=cls.ingredient3, amount=3)

        cls.recipe2: Recipe = Recipe.objects.create(
            author=cls.author, name='Тест Рецепт Другой', text='Много',
            cooking_time=37, image=cls.uploaded
        )
        RecipeTag.objects.create(
            recipe=cls.recipe2, tag=cls.tag1)
        RecipeTag.objects.create(
            recipe=cls.recipe2, tag=cls.tag2)
        RecipeIngredientAmount.objects.create(
            recipe=cls.recipe2, ingredient=cls.ingredient1, amount=4)
        RecipeIngredientAmount.objects.create(
            recipe=cls.recipe2, ingredient=cls.ingredient2, amount=5)
        RecipeIngredientAmount.objects.create(
            recipe=cls.recipe2, ingredient=cls.ingredient3, amount=6)

        cls.recipe3: Recipe = Recipe.objects.create(
            author=cls.author, name='Тест Рецепт Другой', text='Много',
            cooking_time=37, image=cls.uploaded
        )
        RecipeTag.objects.create(
            recipe=cls.recipe3, tag=cls.tag1)
        RecipeTag.objects.create(
            recipe=cls.recipe3, tag=cls.tag2)
        RecipeIngredientAmount.objects.create(
            recipe=cls.recipe3, ingredient=cls.ingredient1, amount=7)
        RecipeIngredientAmount.objects.create(
            recipe=cls.recipe3, ingredient=cls.ingredient2, amount=8)
        RecipeIngredientAmount.objects.create(
            recipe=cls.recipe3, ingredient=cls.ingredient3, amount=9)

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
            HTTP_AUTHORIZATION='Token ' + SubscribesTest.token1.key)

        self.auth_client2 = APIClient()
        self.auth_client2.credentials(
            HTTP_AUTHORIZATION='Token ' + SubscribesTest.token2.key)

        self.author_client = APIClient()
        self.author_client.credentials(
            HTTP_AUTHORIZATION='Token ' + SubscribesTest.token_author.key)

    def test_api_recipes_subscribe(self):
        '''
        Тестируем рецепты в подписках.
        '''

        author = User.objects.get(username='usertest3')
        url = f'/api/users/{author.id}/subscribe/'
        count_subscrybe = SubscribeUser.objects.count()

        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(SubscribeUser.objects.count(), count_subscrybe)

        resp = self.auth_client1.post(url)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SubscribeUser.objects.count(), count_subscrybe + 1)

        try:
            resp_data: dict = resp.json()
        except Exception as err:
            self.assertTrue(
                True,
                msg=f'responce data is not json: {err}'
            )
        self.assertIsInstance(resp_data, dict, 'В ответе не dict')

        fields_name = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]
        for field in fields_name:
            with self.subTest(field=field):
                self.assertIn(
                    field, resp_data, f'в ответе ключ {field} отсутствует.')

        resp = self.auth_client1.post(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(SubscribeUser.objects.count(), count_subscrybe + 1)

        count_subscrybe = SubscribeUser.objects.count()

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(SubscribeUser.objects.count(), count_subscrybe)

        resp = self.auth_client2.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(SubscribeUser.objects.count(), count_subscrybe)

        resp = self.auth_client1.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SubscribeUser.objects.count(), count_subscrybe - 1)
