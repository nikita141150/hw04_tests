from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
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
            text='Текст ТЕСТОВЫЙ',
            id=1,
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

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        count = Post.objects.count()
        form_data = {
            'group': PostCreateFormTests.group.id,
            'text': 'Тестовый текст',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('posts:profile',
                    kwargs={'username': PostCreateFormTests.author.username})
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), count + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.get(text='Тестовый текст'))

    def test_edit_post(self):
        """Проверка формы редактирования поста, изменение его в базе данных."""
        form_data = {
            'group': PostCreateFormTests.group.id,
            'text': 'ИЗМЕНЕННЫЙ ТЕКСТ',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostCreateFormTests.post.id}),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    kwargs={'post_id': PostCreateFormTests.post.id})
        )
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.get(text='ИЗМЕНЕННЫЙ ТЕКСТ'))
