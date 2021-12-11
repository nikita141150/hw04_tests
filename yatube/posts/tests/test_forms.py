from django.test import Client, TestCase
from django.urls import reverse
from django import forms

import uuid

from ..models import Group, Post, User

CREATE_PAGE = reverse('posts:post_create')


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

        self.POST_DETAIL = reverse('posts:post_detail',
                                   kwargs={'post_id': self.post.id})
        self.PROFILE_USER = reverse('posts:profile',
                                    kwargs={'username': self.author.username})
        self.EDIT_PAGE = reverse('posts:post_edit',
                                 kwargs={'post_id': self.post.id})

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        count = Post.objects.count()
        unique_text = uuid.uuid4()
        set_posts_before = set()
        for post in Post.objects.all():
            set_posts_before.add(post.pk)
        form_data = {
            'group': self.group.id,
            'text': str(unique_text),
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            CREATE_PAGE,
            data=form_data,
            follow=True
        )
        # Создаем множество после создания поста
        set_posts_after = set()
        for post in Post.objects.all():
            set_posts_after.add(post.pk)
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
            self.PROFILE_USER
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), count + 1)
        # Проверяем, что в БД есть запись c заданными атрибутами
        self.assertEqual(len(difference_set_after_add_post), 1)
        self.assertEqual(len(difference_set_before_add_post), 0)
        # Проверяем, что в БД занесена запись с нашим текстом
        # Вычисляем pk добавленной записи
        for i in difference_set_after_add_post:
            self.assertEqual(Post.objects.filter(pk=i,
                             text=unique_text).count(), 1)

    def test_edit_post(self):
        """Проверка формы редактирования поста, изменение его в базе данных."""
        # Проверяем количество постов до редактирования записи
        count_before_edit = Post.objects.count()
        unique_text = uuid.uuid4()
        form_data = {
            'group': self.group2.id,
            'text': str(unique_text),
        }
        # Находим pk изменяемой записи
        for post in Post.objects.filter(id=self.post.id):
            pk_post = post.pk
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            self.EDIT_PAGE,
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            self.POST_DETAIL)
        # Проверяем количество постов после редактирования записи
        count_after_edit = Post.objects.count()
        # Проверяем, изменилось ли кол-во постов
        self.assertEqual(count_before_edit, count_after_edit)
        # Проверяем измененную запись
        for post_edit in Post.objects.filter(pk=pk_post):
            self.assertEqual(post_edit.text, str(unique_text))
            self.assertEqual(post_edit.group.id, self.group2.id)

    # Проверяем, что словарь context страницы posts/post_edit
    # содержит ожидаемые значения
    def test_post_edit_page_show_correct_context(self):
        """Шаблон posts/post_edit сформирован с правильным контекстом."""
        urls = [
            self.EDIT_PAGE,
            CREATE_PAGE
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
