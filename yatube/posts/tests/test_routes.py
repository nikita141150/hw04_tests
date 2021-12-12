from django.test import TestCase
from django.urls import reverse

USERNAME = 'man'
POST_ID = 1
SLUG = 'test-slug'


class TestsRoutes(TestCase):

    def test_routes(self):
        urls = [
            ['index', '', '/'],
            ['profile', {'username': USERNAME}, f'/profile/{USERNAME}/'],
            ['post_detail', {'post_id': POST_ID}, f'/posts/{POST_ID}/'],
            ['group_list', {'slug': SLUG}, f'/group/{SLUG}/'],
            ['post_create', '', '/create/'],
            ['post_edit', {'post_id': POST_ID}, f'/posts/{POST_ID}/edit/']
        ]
        for name_route, params, url in urls:
            if params == '':
                self.assertEqual(
                    reverse('posts:' + name_route), url
                )
            self.assertEqual(
                reverse('posts:' + name_route, kwargs=params), url)
