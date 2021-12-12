from django.test import TestCase
from django.urls import reverse

USERNAME = 'man'
POST_ID = 1
GROUP_SLUG = 'test-slug'


class TestsRoutes(TestCase):

    def test_routes(self):
        urls = [
            ['posts:index', '', '', '/'],
            ['posts:profile', 'username', USERNAME, '/profile/man/'],
            ['posts:post_detail', 'post_id', POST_ID, '/posts/1/'],
            ['posts:group_list', 'slug', GROUP_SLUG, '/group/test-slug/'],
            ['posts:post_create', '', '', '/create/'],
            ['posts:post_edit', 'post_id', POST_ID, '/posts/1/edit/']
        ]
        for url in urls:
            if url[1] == '':
                self.assertEqual(
                    reverse(url[0]), url[3]
                )
            else:
                self.assertEqual(
                    reverse(url[0], kwargs={url[1]: url[2]}),
                    url[3]
                )
