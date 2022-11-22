from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test_name',
        )
        cls.user_2 = User.objects.create_user(
            username='test_name_2',
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )
        cls.post_2 = Post.objects.create(
            text='Тестовый текст 2',
            author=cls.user_2,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_client(self):
        """
        Страницы index, group_list, profile, posts_detail
        доступны любому пользователю.
        """
        field_guest = {
            self.guest_client.get('/'): HTTPStatus.OK,
            self.guest_client.get('/group/test-slug/'): HTTPStatus.OK,
            self.guest_client.get('/profile/test_name/'): HTTPStatus.OK,
            self.guest_client.get(f'/posts/{self.post.id}/'): HTTPStatus.OK,
        }
        for field, expected_value in field_guest.items():
            with self.subTest(field=field):
                self.assertEqual(
                    field.status_code, expected_value)

    def test_authorized_client(self):
        """
        Страницы post_edit, posts_create
        доступны авторизованному пользователю.
        """
        field_guest = {
            self.authorized_client.get(
                f'/posts/{self.post.id}/edit/'
            ): HTTPStatus.OK,
            self.authorized_client.get('/create/'): HTTPStatus.OK,
        }
        for field, expected_value in field_guest.items():
            with self.subTest(field=field):
                self.assertEqual(
                    field.status_code, expected_value)

    def test_posts_edit_posts_create_redirect_anonymous_on_admin_login(self):
        """
        Страницы post_edit, posts_create
        перенаправят анонимного пользователя.
        """
        field_guest = {
            self.guest_client.get(
                f'/posts/{self.post.id}/edit/'
            ): HTTPStatus.FOUND,
            self.guest_client.get('/create/'): HTTPStatus.FOUND,
        }
        for field, expected_value in field_guest.items():
            with self.subTest(field=field):
                self.assertEqual(
                    field.status_code, expected_value)

    def test_posts_edit_url_redirect_not_author(self):
        """
        Страница post_edit перенаправит авторизированного
        пользователя, но не автора поста.
        """
        response = self.authorized_client.get(
            f'/posts/{self.post_2.id}/edit/'
        )
        self.assertEqual(response.status_code, 302)

    def test_unexisting_page_url_redirect_anonymous_on_admin_login(self):
        """
        Страница unexisting_page вернет
        неавторизированному пользователю ошибку 404.
        """
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/test_name/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
