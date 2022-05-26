from django.test import TestCase
from users.models import SubscribeUser, User


class UserModelsTest(TestCase):
    '''
    Тестируем модель User.
    '''
    @classmethod
    def setUpClass(cls):
        '''
        Создаём 1 экземпляр модели User.
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

    def test_users_models_user_have_correct_verbose_name(self):
        '''
        Пробежимся по полям модели User и проверим verbose_name.
        '''
        field_verboses = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Адрес электронной почты',
            'username': 'Уникальный юзернейм',
        }
        user: User = UserModelsTest.user
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    user._meta.get_field(field).verbose_name,
                    expected_value, (
                        'Тест не пройден, '
                        f'{user._meta.get_field(field).verbose_name} '
                        f'вместо {expected_value}'
                    )
                )

    def test_users_models_user_have_correct_help_text(self):
        '''
        Пробежимся по полям модели User и проверим help_text.
        '''
        field_help_text = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Адрес электронной почты',
            'username': 'Уникальный юзернейм',
        }
        user: User = UserModelsTest.user
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    user._meta.get_field(field).help_text,
                    expected_value,
                    (
                        'Тест не пройден, '
                        f'{user._meta.get_field(field).help_text} '
                        f'вместо {expected_value}'
                    )
                )

    def test_users_models_user_have_correct_max_length(self):
        '''
        Пробежимся по полям модели User и проверим max_length.
        '''
        field_max_length = {
            'first_name': 150,
            'last_name': 150,
            'username': 150,
        }
        user: User = UserModelsTest.user
        for field, expected_value in field_max_length.items():
            with self.subTest(field=field):
                self.assertEqual(
                    user._meta.get_field(field).max_length,
                    expected_value,
                    (
                        'Тест не пройден, '
                        f'{user._meta.get_field(field).max_length} '
                        f'вместо {expected_value}'
                    )
                )

    def test_tags_models_tag_have_correct_unique(self):
        '''
        Пробежимся по полям модели User и проверим unique.
        '''
        field_unique = {
            'email': True,
            'username': True,
        }
        user: User = UserModelsTest.user
        for field, expected_value in field_unique.items():
            with self.subTest(field=field):
                self.assertEqual(
                    user._meta.get_field(field).unique,
                    expected_value,
                    (
                        'Тест не пройден, '
                        f'{user._meta.get_field(field).unique} '
                        f'вместо {expected_value}'
                    )
                )


class SubscribeUserModelsTest(TestCase):
    '''
    Тестируем модель SubscribeUser.
    '''
    @classmethod
    def setUpClass(cls):
        '''
        Создаём 2 экземпляр модели User и 1 SubscribeUser.
        '''
        super().setUpClass()

        cls.USER_DATA_1 = {
            'first_name': 'Тест',
            'last_name': 'Тестович',
            'email': 'test1@test_domain.info',
            'username': 'usertest1',
            'password': 'test_123',
        }
        cls.USER_DATA_2 = {
            'first_name': 'Тест',
            'last_name': 'Тестович',
            'email': 'test2@test_domain.info',
            'username': 'usertest2',
            'password': 'test_123',
        }
        cls.user = User.objects.create_user(**cls.USER_DATA_1)
        cls.author = User.objects.create_user(**cls.USER_DATA_2)

        cls.subscribe = SubscribeUser.objects.create(
            user=cls.user, author=cls.author)

    def test_users_models_user_have_correct_fields(self):
        '''
        Пробежимся по полям модели User и проверим поля.
        '''
        subscribe: SubscribeUser = SubscribeUserModelsTest.subscribe

        field_verboses = {
            'user': 'Подписки пользователя',
            'author': 'Автор',
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    subscribe._meta.get_field(field).verbose_name,
                    expected_value, (
                        'Некореектный verbose_name, '
                        f'{subscribe._meta.get_field(field).verbose_name} '
                        f'вместо {expected_value}'
                    )
                )

        field_help_text = {
            'user': 'Подписки пользователя',
            'author': 'Автор, на которого подписаны',
        }

        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    subscribe._meta.get_field(field).help_text,
                    expected_value,
                    (
                        'Некореектный help_text, '
                        f'{subscribe._meta.get_field(field).help_text} '
                        f'вместо {expected_value}'
                    )
                )
