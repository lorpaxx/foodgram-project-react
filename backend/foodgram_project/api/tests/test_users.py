from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase
from users.models import SubscribeUser

User = get_user_model()


def add_num_to_value(d: dict, value: int):
    res = {}
    for key, val in d.items():
        res[key] = val + str(value)
    return res


class UsersTests(APITestCase):
    '''
    Тестируем /api/users/.
    '''
    @classmethod
    def setUpClass(cls):
        '''
        Создаём 3 экземпляров модели User.
        '''
        super().setUpClass()
        cls.USER_DATA = {
            'first_name': 'Тест',
            'last_name': 'Тестович',
            'email': 'test@testdomain.info',
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

        cls.subscribe = SubscribeUser.objects.create(
            user=cls.user2, author=cls.author)

        cls.url = '/api/users/'

    def setUp(self):
        '''
        Создадим клиенты для каждого теста.
        '''
        self.client = APIClient()

        self.auth_client1 = APIClient()
        self.auth_client1.credentials(
            HTTP_AUTHORIZATION='Token ' + UsersTests.token1.key)

        self.auth_client2 = APIClient()
        self.auth_client2.credentials(
            HTTP_AUTHORIZATION='Token ' + UsersTests.token2.key)

        self.author_client = APIClient()
        self.author_client.credentials(
            HTTP_AUTHORIZATION='Token ' + UsersTests.token_author.key)

    def test_api_users_01_url_list_and_retrieve_ok(self):
        '''
        Проверяем доступность общедоступных url.
        '''
        urls = [
            UsersTests.url,
            UsersTests.url + f'{UsersTests.user1.id}/',
            UsersTests.url + f'{UsersTests.user2.id}/',
            UsersTests.url + f'{UsersTests.author.id}/',
        ]

        for url in urls:
            with self.subTest(url=url):
                resp = self.client.get(url)
                self.assertEqual(
                    resp.status_code, status.HTTP_200_OK,
                    'status code не совпадает с ожидаемым'
                )

    def test_api_users_02_url_not_auth(self):
        '''
        Проверяем недоступность необщедоступных url.
        '''
        urls = [
            UsersTests.url + 'me/',
        ]

        for url in urls:
            with self.subTest(url=url):
                resp = self.client.get(url)
                self.assertEqual(
                    resp.status_code, status.HTTP_401_UNAUTHORIZED,
                    'status code не совпадает с ожидаемым'
                )

    def test_api_users_03_url_not_found(self):
        '''
        Проверяем недоступность необщедоступных url.
        '''
        urls = [
            UsersTests.url + '4/',
        ]

        for url in urls:
            with self.subTest(url=url):
                resp = self.client.get(url)
                self.assertEqual(
                    resp.status_code, status.HTTP_404_NOT_FOUND,
                    'status code не совпадает с ожидаемым'
                )

    def test_api_users_04_url_test_retrieve(self):
        '''
        Тестируем '/api/users/{id}/.
        '''
        user: User = UsersTests.user2
        url = UsersTests.url + f'{user.id}/'
        resp = self.client.get(url)
        try:
            resp_data: dict = resp.json()
        except Exception as err:
            self.assertTrue(
                True,
                msg=f'responce data is not json: {err}'
            )
        fields_name = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'is_subscribed': False,
        }
        self.assertIsInstance(
            resp_data, dict,
            'В ответе не dict'
        )
        self.assertEqual(
            len(resp_data), len(fields_name),
            'В ответе число ключей отличается.'
        )
        for field in fields_name:
            with self.subTest(field=field):
                self.assertEqual(
                    resp_data[field], fields_name[field],
                    f'в ответе {field} не совпадает с ожидаемым.'
                )

    def test_api_users_05_url_test_list(self):
        '''
        Тестируем '/api/users/.
        '''
        url = UsersTests.url
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
            len(result), 3, 'В result неожиданное число пользователей')

        users = {
            UsersTests.user1.id: UsersTests.user1,
            UsersTests.user2.id: UsersTests.user2,
            UsersTests.author.id: UsersTests.author
        }
        for row in result:
            with self.subTest(row=row):
                fields_name = [
                    'id',
                    'email',
                    'first_name',
                    'last_name',
                    'username',
                ]
                self.assertIsInstance(
                    row, dict,
                    ''
                )
                self.assertEqual(
                    len(fields_name) + 1, len(row),
                    'Число ключей отличается.'
                )
                for field in fields_name:
                    self.assertIn(
                        field, row,
                        f'{field} нет в ответе'
                    )
                user = users[row.get('id')]
                fields_name = {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username,
                    'is_subscribed': False,
                }
                for field in fields_name:
                    self.assertEqual(
                        row[field], fields_name[field],
                        f'В ответе {field} не совпадает с ожидаемым'
                    )

    def test_api_users_06_url_test_create_valid(self):
        '''
        Тестируем /api/users/ создание пользователей.
        '''
        user_data = {
            'first_name': 'Тест',
            'last_name': 'Тестович',
            'email': 'test4@testdomain.info',
            'username': 'usertest4',
            'password': 'test_123',
        }
        url = UsersTests.url
        resp = self.client.post(url, data=user_data, format='json')
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
        self.assertIsInstance(
            resp_data, dict,
            'В ответе ожидали dict'
        )
        fields_name = ['first_name', 'last_name', 'email', 'username', 'id']
        self.assertEqual(
            len(fields_name), len(resp_data),
            'В ответе не то число ключей'
        )
        for field in fields_name:
            with self.subTest(field=field):
                self.assertIn(field, resp_data, f'{field} нет среди ключей')
        user = User.objects.get(username=user_data['username'])

        for field in fields_name:
            with self.subTest(field=field):
                self.assertEqual(
                    resp_data[field], getattr(user, field),
                    f'В ответе ключ {field} не совпадает с ожидаемым.'
                )

    def test_api_users_07_url_test_create_invalid(self):
        user_data = {
            'first_name': 'Тест',
            'last_name': 'Тестович',
            'email': 'test5@testdomain.info',
            'username': 'usertest5',
            'password': 'test_123',
        }
        url = UsersTests.url
        for field in user_data:
            with self.subTest(field=field):
                user_data_sub = user_data.copy()
                user_data_sub.pop(field)
                resp = self.client.post(url, data=user_data_sub, format='json')

                self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

                try:
                    resp_data: dict = resp.json()
                except Exception as err:
                    self.assertTrue(
                        True,
                        msg=f'responce data is not json: {err}'
                    )

                self.assertIsInstance(resp_data, dict)

                self.assertIn(field, resp_data)

    def test_api_users_08_url_test_is_subscribed(self):
        '''
        Проверяем коррестоность работы поля is_subscribed.
        '''
        url = UsersTests.url

        user_data = {
            UsersTests.user1: False,
            UsersTests.user2: False,
            UsersTests.author: False,
        }
        for user, value in user_data.items():
            with self.subTest(user=user, value=value):
                resp = self.auth_client1.get(url + f'{user.id}/')
                self.assertEqual(
                    resp.json().get('is_subscribed'), value)

        user_data = {
            UsersTests.user1: False,
            UsersTests.user2: False,
            UsersTests.author: True,
        }
        for user, value in user_data.items():
            with self.subTest(user=user, value=value):
                resp = self.auth_client2.get(url + f'{user.id}/')
                self.assertEqual(
                    resp.json().get('is_subscribed'), value,
                    f'{user} {value}'
                )

        user_data = {
            UsersTests.user1: False,
            UsersTests.user2: False,
            UsersTests.author: False,
        }
        for user, value in user_data.items():
            with self.subTest(user=user, value=value):
                resp = self.author_client.get(url + f'{user.id}/')
                self.assertEqual(
                    resp.json().get('is_subscribed'), value)

    def test_api_users_09_url_test_me(self):
        '''
        Проверяем работу /api/users/me.
        '''
        url = UsersTests.url + 'me/'
        resp = self.client.get(url)
        self.assertEqual(
            resp.status_code, status.HTTP_401_UNAUTHORIZED,
            'для гостевого пользователя в ответе неожиданный status code'
        )

        resp = self.auth_client2.get(url)
        self.assertEqual(
            resp.status_code, status.HTTP_200_OK,
            'для auth пользователя в ответе неожиданный status code'
        )
        try:
            resp_data: dict = resp.json()
        except Exception as err:
            self.assertTrue(
                True,
                msg=f'responce data is not json: {err}'
            )

        self.assertIsInstance(resp_data, dict)
        user = UsersTests.user2
        fields_name = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'is_subscribed': False,
        }
        self.assertEqual(
            len(resp_data), len(fields_name),
            'В ответе число ключей отличается.'
        )
        for field in fields_name:
            with self.subTest(field=field):
                self.assertEqual(
                    resp_data[field], fields_name[field],
                    f'в ответе {field} не совпадает с ожидаемым.'
                )

    def test_api_users_10_url_test_set_password(self):
        '''
        Тестируем смену пароля для /api/users/set_password/.
        '''
        url = UsersTests.url + 'set_password/'

        valid_data = {
            "new_password": "test_12311",
            "current_password": "test_1231"
        }
        resp = self.client.post(url, data=valid_data, format='json')
        self.assertEqual(
            resp.status_code, status.HTTP_401_UNAUTHORIZED,
            'Для гостевого пользователя неожиданный статус код'
        )

        invalid_data = {
            "new_password": "test_12311",
        }
        resp = self.auth_client1.post(url, data=invalid_data, format='json')
        self.assertEqual(
            resp.status_code, status.HTTP_400_BAD_REQUEST,
            'Для авторизированного пользователя неожиданный статус код'
        )
        self.assertIn(
            'current_password', resp.json()
        )

        invalid_data = {
            "current_password": "test_123"
        }
        resp = self.auth_client1.post(url, data=invalid_data, format='json')
        self.assertEqual(
            resp.status_code, status.HTTP_400_BAD_REQUEST,
            'Для авторизированного пользователя неожиданный статус код'
        )
        self.assertIn(
            'new_password', resp.json()
        )

        resp = self.auth_client1.post(url, data=valid_data, format='json')
        self.assertEqual(
            resp.status_code, status.HTTP_204_NO_CONTENT,
            'Для авторизированного пользователя неожиданный статус код'
        )
