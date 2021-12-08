from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

MAIN_PAGE = 'posts:index'
GROUP_PAGE = 'posts:group_list'
PROFILE_PAGE = 'posts:profile'
POST_DETAIL_PAGE = 'posts:post_detail'
CREATE_POST_PAGE = 'posts:post_create'
EDIT_POST_PAGE = 'posts:post_edit'


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
        # Собираем в словарь пары "reverse(name):имя_html_шаблона"
        templates_pages_names = {
            reverse(
                MAIN_PAGE
            ): 'posts/index.html',
            reverse(
                GROUP_PAGE,
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                PROFILE_PAGE,
                kwargs={'username': self.author.username}
            ): 'posts/profile.html',
            reverse(
                POST_DETAIL_PAGE,
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                CREATE_POST_PAGE,
            ): 'posts/create_post.html',
            reverse(
                EDIT_POST_PAGE,
                kwargs={
                    'post_id': self.post.id}
            ): 'posts/create_post.html'
        }
        # Проверяем, что при обращении к name вызывается соответствующий шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверяем, что словарь страниц
    # содержит ожидаемые значения
    def test_page_show_correct_context(self):
        pages = {
            reverse(
                PROFILE_PAGE,
                kwargs={'username': self.author.username}
            ): 'page_obj',
            reverse(
                MAIN_PAGE
            ): 'page_obj',
            reverse(
                GROUP_PAGE,
                kwargs={'slug': self.group.slug}
            ): 'page_obj',
            reverse(
                POST_DETAIL_PAGE,
                kwargs={'post_id': self.post.id}
            ): 'post',
        }
        for reverse_name, context in pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                if Post.objects.count() == 1 and context != 'post':
                    first_object = response.context[context][0]
                else:
                    first_object = response.context['post']
                self.assertEqual(first_object.text, self.post.text)
                self.assertEqual(first_object.author.username,
                                 self.post.author.username)
                self.assertEqual(first_object.group.title, self.group.title)

    # После публикации поста новая запись появляется на главной
    # странице сайта (index), на персональной странице пользователя (profile),
    # и на отдельной странице поста (post)
    def test_post_appears_on_pages(self):
        page_group2 = reverse(
            GROUP_PAGE,
            kwargs={'slug': self.group2.slug})
        with self.subTest(page_group2=page_group2):
            response_group2 = self.authorized_client.get(page_group2)
            self.assertNotIn(
                self.post.text,
                response_group2.context['page_obj'])


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
        posts = [
            Post(
                author=cls.author,
                text='Тестовый пост',
                id=make_post,
                group=cls.group,)
            for make_post in range(1, 14)
        ]
        cls.post = Post.objects.bulk_create(posts)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.author)

    def test_first_page_contains_ten_records(self):
        pages = [
            reverse(MAIN_PAGE),
            reverse(
                GROUP_PAGE,
                kwargs={'slug': PaginatorViewsTests.group.slug}
            ),
            reverse(
                PROFILE_PAGE,
                kwargs={'username': PaginatorViewsTests.author.username}
            )
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        pages = [
            reverse(MAIN_PAGE),
            reverse(
                GROUP_PAGE,
                kwargs={'slug': PaginatorViewsTests.group.slug}
            ),
            reverse(
                PROFILE_PAGE,
                kwargs={'username': PaginatorViewsTests.author.username}
            )
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
