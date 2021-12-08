from django.test import Client, TestCase
from django.urls import reverse
from django import forms

import uuid

from ..models import Group, Post, User

PROFILE_USER_PAGE = 'posts:profile'
POST_CREATE_PAGE = 'posts:post_create'
POST_EDIT_PAGE = 'posts:post_edit'
POST_DETAIL_PAGE = 'posts:post_detail'


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
        unique_text = uuid.uuid4()
        while Post.objects.filter(text=str(unique_text)).count() > 0:
            unique_text == uuid.uuid4()
        # Создаем множество до создания поста
        set_posts_before = set()
        for post in Post.objects.all():
            set_posts_before.add(str(post))
        form_data = {
            'group': self.group.id,
            'text': str(unique_text),
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse(POST_CREATE_PAGE),
            data=form_data,
            follow=True
        )
        # Создаем множество после создания поста
        set_posts_after = set()
        for post in Post.objects.all():
            set_posts_after.add(str(post))
        # Ищем разность множеств -  результатом
        # является множество, содержащее элементы,
        # которые есть в "уменьшаемом", но их нет в "вычитаемом"
        difference_set_after_add_post = set_posts_after - set_posts_before
        # Ищем разность множеств -  результатом
        # является множество, содержащее элементы,
        # которые есть в "уменьшаемом", но их нет в "вычитаемом"
        difference_set_before_add_post = set_posts_before - set_posts_after
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse(PROFILE_USER_PAGE,
                    kwargs={'username': self.author.username})
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), count + 1)
        # Проверяем, что в БД есть запись c заданными атрибутами
        self.assertEqual(len(difference_set_after_add_post), 1)
        self.assertEqual(len(difference_set_before_add_post), 0)

    def test_edit_post(self):
        """Проверка формы редактирования поста, изменение его в базе данных."""
        # Проверяем количество постов до редактирования записи
        count_before_edit = Post.objects.count()
        unique_text = uuid.uuid4()
        form_data = {
            'group': self.group2.id,
            'text': str(unique_text),
        }
        # Создаем множество до изменения поста
        set_posts_before = set()
        for post in Post.objects.all():
            set_posts_before.add(str(post))
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse(
                POST_EDIT_PAGE,
                kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse(POST_DETAIL_PAGE,
                    kwargs={'post_id': self.post.id}))
        # Создаем множество после изменения поста
        set_posts_after = set()
        for post in Post.objects.all():
            set_posts_after.add(str(post))
        # Проверяем количество постов до редактирования записи
        count_after_edit = Post.objects.count()
        # Ищем разность множеств -  результатом
        # является множество, содержащее элементы,
        # которые есть в "уменьшаемом", но их нет в "вычитаемом"
        difference_set_after_edit_post = set_posts_after - set_posts_before
        # Ищем разность множеств -  результатом
        # является множество, содержащее элементы,
        # которые есть в "уменьшаемом", но их нет в "вычитаемом"
        difference_set_before_edit_post = set_posts_before - set_posts_after
        # Проверяем, изменился ли пост
        self.assertEqual(count_before_edit, count_after_edit)
        self.assertEqual(len(difference_set_after_edit_post), 1)
        self.assertEqual(len(difference_set_before_edit_post), 1)

    # Проверяем, что словарь context страницы posts/post_edit
    # содержит ожидаемые значения
    def test_post_edit_page_show_correct_context(self):
        """Шаблон posts/post_edit сформирован с правильным контекстом."""
        pages = [
            reverse(
                POST_EDIT_PAGE,
                kwargs={'post_id': self.post.id}),
            reverse(
                POST_CREATE_PAGE)
        ]
        for page in pages:
            response = self.authorized_client.get(page)
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
