from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Group, Post, User

MAIN_PAGE = '/'
GROUP_PAGE = '/group/test-slug/'
PROFILE_PAGE = '/profile/auth/'
POST_PAGE = '/posts/1/'
POST_EDIT_PAGE = '/posts/1/edit/'
POST_EDIT_PAGE_REDIRECT = '/auth/login/?next=/posts/1/edit/'
CREATE_PAGE = '/create/'
UNKNOWN_PAGE = '/unexisting_page/'


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
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.author)

    def test_pages(self):
        pages_test_guest = [MAIN_PAGE, GROUP_PAGE, PROFILE_PAGE, POST_PAGE]
        pages_test_authorized = [POST_EDIT_PAGE, CREATE_PAGE]
        for page in pages_test_guest:
            self.assertEqual(self.guest_client.get(page).status_code,
                             HTTPStatus.OK)
        for page in pages_test_authorized:
            self.assertEqual(self.authorized_client.get(page).status_code,
                             HTTPStatus.OK)

        self.assertRedirects(
            self.guest_client.get(POST_EDIT_PAGE, follow=True),
            POST_EDIT_PAGE_REDIRECT
        )
        self.assertEqual(self.guest_client.get(UNKNOWN_PAGE).status_code,
                         HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            MAIN_PAGE: 'posts/index.html',
            GROUP_PAGE: 'posts/group_list.html',
            PROFILE_PAGE: 'posts/profile.html',
            POST_PAGE: 'posts/post_detail.html',
            CREATE_PAGE: 'posts/create_post.html',
            POST_EDIT_PAGE: 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                self.assertTemplateUsed(
                    self.authorized_client.get(adress),
                    template
                )
