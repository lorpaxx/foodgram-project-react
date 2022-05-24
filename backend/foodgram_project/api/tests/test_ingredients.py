from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class TagsTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        '''
        Создаём 1 экземпляр модели Post.
        '''
        super().setUpClass()
        cls.user = User.objects.create_user(username='usertest')
        cls.token = Token.objects.create(user=cls.user)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            user=TagsTests.user, token=TagsTests.token.key
        )

    def test_tag(self):
        # client = APIClient()
        # responce = client.get('/api/tags/')
        # self.assertEqual(responce.status_code, 200, 'test 1')
        # client.force_authenticate(
        #     token='38d331125b8637e7d9658c035601befd5763176f'
        # )
        # client.credentials(
        #     HTTP_AUTHORIZATION='Token 38d331125b8637e7d9658c035601befd5763176f'
        # )
        responce = self.client.get('/api/users/subscriptions/')
        self.assertEqual(responce.status_code, 200, 'test 2')
