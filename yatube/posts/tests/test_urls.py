from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

from ..models import Group, Post, User

MAIN_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
UNKNOWN_URL = '/unexisting_page/'
PROFILE_URL = reverse('posts:profile',
                      kwargs={'username': 'auth'})
GROUP_URL = reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'})


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
        cls.POST_DETAIL_URL = reverse('posts:post_detail',
                                      kwargs={'post_id': cls.post.id})
        cls.POST_EDIT_URL = reverse('posts:post_edit',
                                    kwargs={'post_id': cls.post.id})

    def setUp(self):
        self.guest = Client()
        self.authorized = Client()
        self.authorized.force_login(self.author)

    def test_urls_show_correct_status(self):
        cases = [
            [MAIN_URL, self.guest, HTTPStatus.OK, '', ''],
            [GROUP_URL, self.guest, HTTPStatus.OK, '', ''],
            [PROFILE_URL, self.guest, HTTPStatus.OK, '', ''],
            [self.POST_DETAIL_URL, self.guest, HTTPStatus.OK, '', ''],
            [self.POST_EDIT_URL, self.authorized, HTTPStatus.OK,
                self.guest, HTTPStatus.FOUND],
            [CREATE_URL, self.authorized, HTTPStatus.OK,
                self.guest, HTTPStatus.FOUND],
            [UNKNOWN_URL, self.guest, HTTPStatus.NOT_FOUND, '', '']
        ]
        for url, client, code, redirect_client, code_redirect in cases:
            self.assertEqual(client.get(url).status_code, code)
            if redirect_client == self.guest:
                self.assertEqual(redirect_client.get(url).status_code,
                                 code_redirect)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            MAIN_URL: 'posts/index.html',
            GROUP_URL: 'posts/group_list.html',
            PROFILE_URL: 'posts/profile.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            CREATE_URL: 'posts/create_post.html',
            self.POST_EDIT_URL: 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.authorized.get(url),
                    template
                )

    def test_urls_make_correct_redirect(self):
        self.guest = Client()
        url_redirect = 'users:login'
        urls = [CREATE_URL, self.POST_EDIT_URL]
        self.new_user = User.objects.create_user(username='somebody')
        self.another = Client()
        self.another.force_login(self.new_user)
        for url in urls:
            redirect_url = reverse(url_redirect) + '?next=' + str(url)
            self.assertRedirects(
                self.guest.get(url, follow=True),
                redirect_url
            )
        self.assertRedirects(
            self.another.get(self.POST_EDIT_URL, follow=True),
            self.POST_DETAIL_URL
        )
