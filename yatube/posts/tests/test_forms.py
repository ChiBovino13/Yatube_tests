from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='NoName',
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовый заголовок 2',
            slug='test-slug-2',
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост 2',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={
                    'username': PostCreateFormTests.user.username
                }
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(Post.objects.first().text, form_data['text'])
        self.assertEqual(Post.objects.first().group.pk, form_data['group'])

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост 3',
            'group': self.group_2.pk,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={
                    'post_id': self.post.id
                }
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={
                    'post_id': self.post.id
                }
            )
        )
        self.assertEqual(self.post.id, PostCreateFormTests.post.id)
        self.assertEqual(
            Post.objects.get(
                id=self.post.id,
            ).text, form_data['text']
        )
        self.assertEqual(
            Post.objects.get(
                id=self.post.id,
            ).group.pk, form_data['group'])
        self.assertEqual(Post.objects.count(), posts_count)
