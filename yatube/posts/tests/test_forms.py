from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post, User

CREATION_URL = reverse('posts:post_create')
PROFILE_USER = reverse('posts:profile',
                       kwargs={'username': 'auth'})


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
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Текст ТЕСТОВЫЙ',
            group=cls.group
        )
        cls.POST_DETAIL = reverse('posts:post_detail',
                                  kwargs={'post_id': cls.post.id})
        cls.EDIT_PAGE = reverse('posts:post_edit',
                                kwargs={'post_id': cls.post.id})

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.author)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        count = Post.objects.count()
        set_posts_before = set()
        for post in Post.objects.all():
            set_posts_before.add(post.pk)
        form_data = {
            'group': self.group.id,
            'text': 'Любой текст',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            CREATION_URL,
            data=form_data,
            follow=True
        )
        # Получаем последний созданный объект
        post = Post.objects.order_by('-pub_date')[0]

        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            PROFILE_USER
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), count + 1)
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.text, 'Любой текст')
        self.assertEqual(post.group.slug, self.group.slug)

    def test_edit_post(self):
        """Проверка формы редактирования поста, изменение его в базе данных."""
        # Проверяем количество постов до редактирования записи
        count_before_edit = Post.objects.count()
        form_data = {
            'group': self.group2.id,
            'text': 'Измененный текст',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            self.EDIT_PAGE,
            data=form_data,
            follow=True
        )
        post = response.context['post']
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            self.POST_DETAIL)
        # Проверяем количество постов после редактирования записи
        count_after_edit = Post.objects.count()
        # Проверяем, изменилось ли кол-во постов
        self.assertEqual(count_before_edit, count_after_edit)
        # Проверяем измененную запись
        self.assertEqual(post.text, 'Измененный текст')
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.group2)

    # Проверяем, что словарь context страницы posts/post_edit
    # содержит ожидаемые значения
    def test_post_edit_page_show_correct_context(self):
        """Шаблон posts/post_edit сформирован с правильным контекстом."""
        urls = [
            self.EDIT_PAGE,
            CREATION_URL
        ]
        for url in urls:
            response = self.authorized_client.get(url)
            # Словарь ожидаемых типов полей формы:
            # указываем, объектами какого класса должны быть поля формы
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)
