from django.test import Client, TestCase
from django.urls import reverse

from ..settings import PAGINATOR_PAGE_SIZE
from ..models import Group, Post, User

MAIN_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')


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
            text='Тестовая запись',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        # Урлы через маршруты
        self.POST_DETAIL = reverse('posts:post_detail',
                                   kwargs={'post_id': self.post.id})
        self.PROFILE_USER = reverse('posts:profile',
                                    kwargs={'username': self.author.username})
        self.EDIT_PAGE = reverse('posts:post_edit',
                                 kwargs={'post_id': self.post.id})
        self.GROUP_URL = reverse('posts:group_list',
                                 kwargs={'slug': self.group.slug})
        self.GROUP_2_URL = reverse('posts:group_list',
                                   kwargs={'slug': self.group2.slug})
        self.PROFILE_URL = reverse('posts:profile',
                                   kwargs={'username': self.author.username})
        self.POST_DETAIL_URL = reverse('posts:post_detail',
                                       kwargs={'post_id': self.post.id})
        self.POST_EDIT_URL = reverse('posts:post_edit',
                                     kwargs={'post_id': self.post.id})

    # Проверяем, что словарь страниц
    # содержит ожидаемые значения
    def test_page_show_correct_context(self):
        urls = {
            MAIN_URL: 'page_obj',
            self.GROUP_URL: 'page_obj',
            self.PROFILE_URL: 'page_obj',
            self.POST_DETAIL_URL: 'post',
        }
        for url, context in urls.items():
            response = self.authorized_client.get(url)
            if context == 'page_obj':
                post_object = response.context[context][0]
            elif context == 'post':
                post_object = response.context[context]
            self.assertEqual(Post.objects.count(), 1)
            self.assertEqual(post_object.pk, self.post.pk)
            self.assertEqual(post_object.text, self.post.text)
            self.assertEqual(post_object.author, self.post.author)
            self.assertEqual(post_object.group.title, self.group.title)

    # После публикации поста новая запись появляется на главной
    # странице сайта (index), на персональной странице пользователя (profile),
    # и на отдельной странице поста (post)
    def test_post_appears_on_pages(self):
        urls = [
            MAIN_URL,
            self.GROUP_URL,
            self.PROFILE_URL
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.context['page_obj'][0].text,
                                 'Тестовая запись')
                self.assertEqual(response.context['page_obj'][0].group.id,
                                 self.group.id)
        self.assertNotIn(
            self.post, self.authorized_client.get(self.GROUP_2_URL).
            context.get('page_obj').object_list)


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
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.GROUP_URL = reverse('posts:group_list',
                                 kwargs={'slug': self.group.slug})
        self.PROFILE_URL = reverse('posts:profile',
                                   kwargs={'username': self.author.username})

    def test_page_contains_records(self):
        urls = [
            MAIN_URL,
            self.GROUP_URL,
            self.PROFILE_URL
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(len(response.context['page_obj']),
                                 PAGINATOR_PAGE_SIZE)
                response = self.authorized_client.get(url + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
