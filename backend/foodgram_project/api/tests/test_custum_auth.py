from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class CustumAuthTest(APITestCase):
    '''
    Тестируем /api/auth/token/.
    '''
    @classmethod
    def setUpClass(cls):
        '''
        Создаём 1 тестового пользователя для всех тестов.
        '''
        super().setUpClass()
        cls.USER_DATA = {
            'first_name': 'Тест',
            'last_name': 'Тестович',
            'email': 'test@test_domain.info',
            'username': 'usertest',
            'password': 'test_123',
        }
        cls.user = User.objects.create_user(**cls.USER_DATA)
        cls.url = '/api/auth/token/'

    def setUp(self):
        '''
        Создадим клиенты для каждого теста.
        '''
        self.client = APIClient()
        self.auth_client = APIClient()

    def test_api_custum_auth_01_get_token_valid_data(self):
        '''
        Тестируем получение токена /api/auth/token/login/ при валидных данных.
        '''
        user = CustumAuthTest.user
        url = CustumAuthTest.url + 'login/'
        user_data = CustumAuthTest.USER_DATA
        valid_data = {
            'password': user_data['password'],
            'email': user_data['email'],
        }
        resp = self.client.post(url, data=valid_data, format='json')

        self.assertEqual(
            resp.status_code, status.HTTP_201_CREATED,
            f'POST на {url} выдаёт неожидаеёмый статус код'
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
            f'В ответе на {url} не dict'
        )

        self.assertEqual(
            len(resp_data), 1,
            'В ответе не один ключ словаря'
        )
        self.assertIsNotNone(
            resp_data.get('auth_token', None),
            'Ключ "auth_token" отсутствует в ответе'
        )
        try:
            token = Token.objects.get(user=user)
        except Exception:
            self.assertTrue(True, 'А токен в базе не создался.')
        self.assertEqual(
            resp_data['auth_token'], token.key,
            'Не верный токен в ответе.'
        )

    def test_api_custum_auth_02_get_token_invalid_data(self):
        '''
        Тестируем получение токена
        /api/auth/token/login/ при инвалидных данных.
        '''
        url = CustumAuthTest.url + 'login/'
        user_data = CustumAuthTest.USER_DATA
        invalid_data = [
            {
                'password_': user_data['password'],
                'email': user_data['email'],
            },
            {
                'password_': user_data['password'],
                'email_': user_data['email'],
            },
            {
                'password': user_data['password'],
            },
            {
                'email': user_data['email'],
            },
            {
                'password': user_data['password'],
                'email': user_data['email'] + '_',
            },
            {
                'password': user_data['password'] + '_',
                'email': user_data['email'],
            },
        ]
        expected_codes = [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_401_UNAUTHORIZED,
        ]
        texts_err = [
            'На ключ password_ не верный status code',
            'На ключ email_ не верный status code',
            'На отсутствие ключа email не верный status code',
            'На отсутствие ключа password не верный status code',
            'На не валидный email не верный status code',
            'На не валидный password не верный status code',
        ]
        for i in range(len(invalid_data)):
            with self.subTest(i=i):
                resp = self.client.post(url, data=invalid_data[i])
                self.assertEqual(
                    resp.status_code, expected_codes[i],
                    texts_err[i]
                )

    def test_api_custum_auth_03_drop_token_valid_data(self):
        '''
        Тестируем удаление токена
        /api/auth/token/logout/ при валидных данных.
        '''
        user = CustumAuthTest.user
        url = CustumAuthTest.url + 'logout/'
        token = Token.objects.create(user=user)

        self.assertEqual(
            Token.objects.filter(user=user).count(), 1,
            'Токен не создался'
        )

        self.auth_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        resp = self.auth_client.post(url)

        self.assertEqual(
            resp.status_code, status.HTTP_204_NO_CONTENT,
            'В ответе от авторизированного пользователя приходит'
            'не ожидаемый status_code'
        )

    def test_api_custum_auth_04_drop_token_invalid_data(self):
        '''
        Тестируем удаление токена
        /api/auth/token/logout/ при инвалидных данных.
        '''
        user = CustumAuthTest.user
        url = CustumAuthTest.url + 'logout/'
        Token.objects.create(user=user)

        resp = self.client.post(url)

        self.assertEqual(
            resp.status_code, status.HTTP_401_UNAUTHORIZED,
            'В ответе не ожидаемый status_code'
        )

        self.assertTrue(
            Token.objects.filter(user=user).exists(),
            'Токен не должен был удалиться из базы.'
        )
