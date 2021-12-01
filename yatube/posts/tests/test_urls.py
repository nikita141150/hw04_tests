from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from http import HTTPStatus

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тест',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='somebody')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_homepage(self):
        # Делаем запрос к главной странице и проверяем статус
        response = self.guest_client.get('/')
        # Утверждаем, что для прохождения теста код должен быть равен 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group(self):
        # Делаем запрос к главной странице и проверяем статус
        response = self.guest_client.get('/group/test-slug/')
        # Утверждаем, что для прохождения теста код должен быть равен 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile(self):
        response = self.guest_client.get('/profile/somebody/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post(self):
        response = self.guest_client.get('/posts/1/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_authorized(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_none_authorized(self):
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/posts/1/edit/'
        )

    def test_post_create(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unknown_page(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/somebody/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            self.authorized_client.force_login(self.author)
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
