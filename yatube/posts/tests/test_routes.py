from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class TestsRoutes(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Текст ТЕСТОВЫЙ',
            group=cls.group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.author)

    def test_routes(self):
        urls = {
            reverse('posts:index'): '/',
            reverse('posts:profile',
                    kwargs={
                        'username': self.author.username
                    }): '/profile/auth/',
            reverse('posts:post_detail',
                    kwargs={
                        'post_id': self.post.id
                    }): '/posts/1/',
            reverse('posts:group_list',
                    kwargs={
                        'slug': self.group.slug
                    }): '/group/test-slug/',
            reverse('posts:post_create'): '/create/',
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': self.post.id
                    }): '/posts/1/edit/'
        }
        for route, url in urls.items():
            with self.subTest(route=route):
                self.assertEqual(
                    route,
                    url
                )
