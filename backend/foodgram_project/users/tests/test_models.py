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
        cls.user = User.objects.create_user(
            username='usertest',
        )

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
        Пробежимся по полям модели Tag и проверим help_text.
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
        Пробежимся по полям модели Tag и проверим max_length.
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
        Пробежимся по полям модели Tag и проверим unique.
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
