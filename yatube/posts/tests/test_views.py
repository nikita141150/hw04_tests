from django.test import Client, TestCase
from django.urls import reverse

from ..settings import PAGINATOR_PAGE_SIZE
from ..models import Group, Post, User

MAIN_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
GROUP_URL = reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'})
GROUP_2_URL = reverse('posts:group_list',
                      kwargs={'slug': 'test-slug2'})
PROFILE_URL = reverse('posts:profile',
                      kwargs={'username': 'auth'})


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
        cls.POST_DETAIL_URL = reverse('posts:post_detail',
                                      kwargs={'post_id': cls.post.id})
        cls.POST_EDIT_URL = reverse('posts:post_edit',
                                    kwargs={'post_id': cls.post.id})

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    # Проверяем, что словарь страниц
    # содержит ожидаемые значения
    def test_page_show_correct_context(self):
        urls = {
            MAIN_URL: 'page_obj',
            GROUP_URL: 'page_obj',
            PROFILE_URL: 'page_obj',
            self.POST_DETAIL_URL: 'post',
        }
        for url, context in urls.items():
            response = self.authorized_client.get(url)
            if context == 'page_obj':
                self.assertEqual(len(response.context[context].object_list),
                                 1)
                post = response.context[context][0]
            elif context == 'post':
                post = response.context[context]
            self.assertEqual(post.pk, self.post.pk)
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.slug, self.group.slug)

    def test_appears_on_page_author(self):
        self.assertEqual(self.author,
                         self.authorized_client.get(PROFILE_URL).context.get
                         ('author'))

    def test_appears_on_page_group(self):
        group = self.authorized_client.get(GROUP_URL).context.get('group')
        self.assertEqual(self.group.title, group.title)
        self.assertEqual(self.group.id, group.id)
        self.assertEqual(self.group.slug, group.slug)
        self.assertEqual(self.group.description, group.description)

    def test_not_appears_on_page_group2(self):
        self.assertNotIn(
            self.post, self.authorized_client.get(GROUP_2_URL).
            context.get('page_obj'))


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
                group=cls.group,)
            for make_post in range(PAGINATOR_PAGE_SIZE + 5)
        ]
        cls.post = Post.objects.bulk_create(posts)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_page_contains_records(self):
        urls = [
            [MAIN_URL, PAGINATOR_PAGE_SIZE],
            [GROUP_URL, PAGINATOR_PAGE_SIZE],
            [PROFILE_URL, PAGINATOR_PAGE_SIZE],
            [MAIN_URL + '?page=2', 5],
            [GROUP_URL + '?page=2', 5],
            [PROFILE_URL + '?page=2', 5]
        ]
        for url, page_size in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(len(response.context['page_obj']),
                                 page_size)
