from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

from ..models import Group, Post, User

MAIN_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
UNKNOWN_URL = '/unexisting_page/'
URL_REDIRECT = '/auth/login/?next='


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
        self.PROFILE_URL = reverse('posts:profile',
                                   kwargs={'username': self.author.username})
        self.POST_DETAIL_URL = reverse('posts:post_detail',
                                       kwargs={'post_id': self.post.id})
        self.POST_EDIT_URL = reverse('posts:post_edit',
                                     kwargs={'post_id': self.post.id})

    def test_urls_show_correct_status(self):
        cases = [
            [MAIN_URL, self.guest_client, HTTPStatus.OK],
            [self.GROUP_URL, self.guest_client, HTTPStatus.OK],
            [self.PROFILE_URL, self.guest_client, HTTPStatus.OK],
            [self.POST_DETAIL_URL, self.guest_client, HTTPStatus.OK],
            [self.POST_EDIT_URL, self.authorized_client, HTTPStatus.OK],
            [CREATE_URL, self.authorized_client, HTTPStatus.OK],
            [UNKNOWN_URL, self.guest_client, HTTPStatus.NOT_FOUND]
        ]
        for case in cases:
            self.assertEqual(case[1].get(case[0]).status_code, case[2])

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            MAIN_URL: 'posts/index.html',
            self.GROUP_URL: 'posts/group_list.html',
            self.PROFILE_URL: 'posts/profile.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            CREATE_URL: 'posts/create_post.html',
            self.POST_EDIT_URL: 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.authorized_client.get(url),
                    template
                )

    def test_urls_make_correct_redirect(self):
        urls = [CREATE_URL, self.POST_EDIT_URL]
        for url in urls:
            redirect_url = URL_REDIRECT + str(url)
            self.assertRedirects(
                self.guest_client.get(url, follow=True),
                (redirect_url)
            )
