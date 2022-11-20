from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test_name',
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            pub_date='01.01.2022',
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_homepage(self):
        """Страница index доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_slug_url_exists_at_desired_location(self):
        """Страница group_list доступна любому пользователю."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_post_profile_url_exists_at_desired_location(self):
        """Страница profile доступна любому пользователю."""
        response = self.guest_client.get('/profile/test_name/')
        self.assertEqual(response.status_code, 200)

    def test_posts_post_id_url_exists_at_desired_location(self):
        """Страница posts_detail доступна любому пользователю."""
        response = self.guest_client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_posts_edit_url_exists_at_desired_location(self):
        """
        Страница post_edit
        доступна авторизованному пользователю.
        """
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_posts_create_url_exists_at_desired_location(self):
        """Страница posts_create доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_posts_edit_url_redirect_anonymous_on_admin_login(self):
        """
        Страница post_edit
        перенаправит анонимного пользователя.
        """
        response = self.guest_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 302)

    def test_posts_create_url_redirect_anonymous_on_admin_login(self):
        """Страница posts_create перенаправит анонимного пользователя."""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, 302)

    def test_unexisting_page_url_redirect_anonymous_on_admin_login(self):
        """
        Страница unexisting_page вернет
        неавторизированному пользователю ошибку 404.
        """
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_unexisting_page_url_redirect_anonymous_on_admin_login(self):
        """
        Страница unexisting_page вернет а
        вторизированному пользователю ошибку 404.
        """
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

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
