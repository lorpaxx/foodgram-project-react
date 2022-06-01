from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from tags.models import Tag


class TagsTests(APITestCase):
    '''
    Тестируем /api/tags/.
    '''
    @classmethod
    def setUpClass(cls):
        '''
        Создаём 5 экземпляров модели Tag.
        '''
        super().setUpClass()
        cls.tag1 = Tag.objects.create(
            name='Tag_1', slug='Tag_1', color='#111111')
        cls.tag2 = Tag.objects.create(
            name='Tag_2', slug='Tag_2', color='#111112')
        cls.tag3 = Tag.objects.create(
            name='Tag_3', slug='Tag_3', color='#111113')

    def setUp(self):
        '''
        Создадим гостевой клиент для каждого теста.
        '''
        self.client = APIClient()

    def test_api_tags_01_url_list(self):
        '''
        Проверяем /api/tags/ доступность всего списка.
        '''
        url = '/api/tags/'
        resp = self.client.get(url)
        self.assertEqual(
            resp.status_code, status.HTTP_200_OK,
        )

    def test_api_tags_02_url_retrieve(self):
        '''
        Проверяем /api/tags/ доступность одного элемента.
        '''
        tag = TagsTests.tag1
        url = f'/api/tags/{tag.id}/'
        resp = self.client.get(url)
        self.assertEqual(
            resp.status_code, status.HTTP_200_OK,
        )

    def test_api_tags_04_retrieve_correct_fields(self):
        '''
        Проверяем /api/tags/{id}/ корректность получаемых данных.
        '''
        tag = TagsTests.tag1
        url = f'/api/tags/{tag.id}/'

        resp = self.client.get(url)
        try:
            resp_data: dict = resp.json()
        except Exception as err:
            self.assertTrue(
                True,
                msg=f'responce data is not json: {err}'
            )
        fields_name = {
            'id': tag.id,
            'name': tag.name,
            'slug': tag.slug,
            'color': tag.color,
        }
        self.assertEqual(
            len(resp_data), len(fields_name),
            'Число полей в ответе не соответствует ожиданиям'
        )
        for field, value in fields_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    resp_data[field],
                    value,
                    f'Поле {field} не верное значение'
                )

    def test_api_tags_05_list_correct(self):
        '''
        Проверяем /api/tags/ корректность получаемых данных.
        '''
        url = '/api/tags/'
        resp = self.client.get(url)
        try:
            resp_data: dict = resp.json()
        except Exception as err:
            self.assertTrue(
                True,
                msg=f'responce data is not json: {err}'
            )
        self.assertIsInstance(resp_data, list, 'В ответе не list')
        self.assertEqual(
            len(resp_data), 3, 'В ответе не то число элементов списка'
        )
        for tag_data in resp_data:
            with self.subTest(tag_data=tag_data):
                self.assertIsInstance(
                    tag_data, dict, 'в ответе не список словарей'
                )
                self.assertIsNotNone(
                    tag_data.get('id', None),
                    'В словаре нет ключа id'
                )
                fields_name = ['name', 'color', 'slug']
                self.assertEqual(
                    len(tag_data), len(fields_name) + 1,
                    'Число ключей в ответе не соответствует ожидаемым'
                )
                id = tag_data.get('id')
                tag = Tag.objects.get(id=id)
                for field_name in fields_name:
                    self.assertEqual(
                        tag_data[field_name], getattr(tag, field_name)
                    )
