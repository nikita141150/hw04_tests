from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post


User = get_user_model()


class ViewsTests(TestCase):
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

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': ViewsTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': ViewsTests.author.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': ViewsTests.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_create'
            ): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': ViewsTests.post.id}
            ): 'posts/create_post.html'
        }
        # Проверяем, что при обращении к name вызывается соответствующий шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверяем, что словарь context страницы posts/index
    # содержит ожидаемые значения
    def test_index_page_show_correct_context(self):
        """Шаблон posts/index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0, ViewsTests.post.text)
        self.assertEqual(post_author_0, ViewsTests.post.author.username)
        self.assertEqual(post_group_0, ViewsTests.group.title)

    # Проверяем, что словарь context страницы posts/group_list
    # содержит ожидаемые значения
    def test_group_list_page_show_correct_context(self):
        """Шаблон posts/group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': ViewsTests.group.slug}
        ))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.slug
        self.assertEqual(post_text_0, ViewsTests.post.text)
        self.assertEqual(post_author_0, ViewsTests.post.author.username)
        self.assertEqual(post_group_0, ViewsTests.group.slug)

    # Проверяем, что словарь context страницы posts/profile
    # содержит ожидаемые значения
    def test_profile_page_show_correct_context(self):
        """Шаблон posts/profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': ViewsTests.author.username}
        ))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0, ViewsTests.post.text)
        self.assertEqual(post_author_0, ViewsTests.post.author.username)
        self.assertEqual(post_group_0, ViewsTests.group.title)

    # Проверяем, что словарь context страницы posts/post_detail
    # содержит ожидаемые значения
    def test_post_detail_page_show_correct_context(self):
        """Шаблон posts/post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': ViewsTests.post.id}
        ))
        first_object = response.context['post']
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0, ViewsTests.post.text)
        self.assertEqual(post_author_0, ViewsTests.post.author.username)
        self.assertEqual(post_group_0, ViewsTests.group.title)

    # Проверяем, что словарь context страницы posts/post_edit
    # содержит ожидаемые значения
    def test_post_edit_page_show_correct_context(self):
        """Шаблон posts/post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': ViewsTests.post.id}))
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

    # Проверяем, что словарь context страницы posts/create
    # содержит ожидаемые значения
    def test_post_create_page_show_correct_context(self):
        """Шаблон posts/create """
        response = self.authorized_client.get(reverse(
            'posts:post_create'))
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

    # После публикации поста новая запись появляется на главной
    # странице сайта (index), на персональной странице пользователя (profile),
    # и на отдельной странице поста (post)
    def test_post_appears_on_pages(self):
        pages = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': ViewsTests.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': ViewsTests.author.username}
            )
        ]
        page_group2 = reverse(
            'posts:group_list',
            kwargs={'slug': ViewsTests.group2.slug})
        with self.subTest(page_group2=page_group2):
            response_group2 = self.authorized_client.get(page_group2)
            self.assertNotIn(
                ViewsTests.post.text,
                response_group2.context['page_obj'])
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                given_text = response.context['page_obj'].object_list[0].text
                given_group = response.context['page_obj'].object_list[0].group
                self.assertEqual(given_text, ViewsTests.post.text)
                self.assertEqual(given_group, ViewsTests.post.group)


class PaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for make_post in range(1, 14):
            cls.post = Post.objects.create(
                author=cls.author,
                text='Тестовый пост',
                id=make_post,
                group=cls.group,
            )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.author)

    def test_first_page_contains_ten_records(self):
        pages = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTests.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTests.author.username}
            )
        ]
        for page in pages:
            response = self.authorized_client.get(page)
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        pages = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTests.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTests.author.username}
            )
        ]
        for page in pages:
            response = self.authorized_client.get(page + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 3)
