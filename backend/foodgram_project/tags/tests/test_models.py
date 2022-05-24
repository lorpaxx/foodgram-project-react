from django.test import TestCase
from tags.models import Tag


class TagModelsTest(TestCase):
    '''
    Тестируем модель Tag.
    '''
    @classmethod
    def setUpClass(cls):
        '''
        Создаём 1 экземпляр модели Tag.
        '''
        super().setUpClass()
        cls.tag = Tag.objects.create(
            name='Tag1',
            slug='Tag_1',
            color='#111111',
        )

    def test_tags_models_tag_have_correct_object_names(self):
        """
        Проверяем, что у модели Tag корректно работает __str__.
        """
        tag: Tag = TagModelsTest.tag
        self.assertEqual(
            str(tag),
            'Tag: Tag_1-#111111',
            'Тест не пройден, __str__ Tag выводит не ожидаемое')

    def test_tags_models_tag_have_correct_verbose_name(self):
        '''
        Пробежимся по полям модели Tag и проверим verbose_name.
        '''
        field_verboses = {
            'name': 'Название',
            'slug': 'Уникальный слаг',
            'color': 'Цвет в HEX'
        }
        tag: Tag = TagModelsTest.tag
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    tag._meta.get_field(field).verbose_name,
                    expected_value, (
                        'Тест не пройден, '
                        f'{tag._meta.get_field(field).verbose_name} '
                        f'вместо {expected_value}'
                    )
                )

    def test_tags_models_tag_have_correct_help_text(self):
        '''
        Пробежимся по полям модели Tag и проверим help_text.
        '''
        field_help_text = {
            'name': 'Название',
            'slug': 'Уникальный слаг',
            'color': 'Цвет в HEX'
        }
        tag: Tag = TagModelsTest.tag
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    tag._meta.get_field(field).help_text,
                    expected_value,
                    (
                        'Тест не пройден, '
                        f'{tag._meta.get_field(field).help_text} '
                        f'вместо {expected_value}'
                    )
                )

    def test_tags_models_tag_have_correct_max_length(self):
        '''
        Пробежимся по полям модели Tag и проверим max_length.
        '''
        field_max_length = {
            'name': 200,
            'slug': 200,
            'color': 7
        }
        tag: Tag = TagModelsTest.tag
        for field, expected_value in field_max_length.items():
            with self.subTest(field=field):
                self.assertEqual(
                    tag._meta.get_field(field).max_length,
                    expected_value,
                    (
                        'Тест не пройден, '
                        f'{tag._meta.get_field(field).max_length} '
                        f'вместо {expected_value}'
                    )
                )

    def test_tags_models_tag_have_correct_unique(self):
        '''
        Пробежимся по полям модели Tag и проверим unique.
        '''
        field_unique = {
            'name': True,
            'slug': True,
            'color': True
        }
        tag: Tag = TagModelsTest.tag
        for field, expected_value in field_unique.items():
            with self.subTest(field=field):
                self.assertEqual(
                    tag._meta.get_field(field).unique,
                    expected_value,
                    (
                        'Тест не пройден, '
                        f'{tag._meta.get_field(field).unique} '
                        f'вместо {expected_value}'
                    )
                )
