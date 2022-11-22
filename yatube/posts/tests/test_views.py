from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from yatube.settings import POSTS_PER_PAGE

from ..models import Group, Post, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='Voland',
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={
                    'slug': PostPagesTests.group.slug
                }
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={
                    'username': PostPagesTests.user.username
                }
            ): 'posts/profile.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={
                    'post_id': PostPagesTests.post.id
                }
            ): 'posts/create_post.html',
            reverse(
                'posts:post_detail', kwargs={
                    'post_id': PostPagesTests.post.id
                }
            ): 'posts/post_detail.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def context_for_all_with_page_obj(self, response):
        if Post.objects.count() >= 1:
            first_object = response.context['page_obj'][0]
            objects = {
                self.post.text: first_object.text,
                self.post.id: first_object.id,
                self.user: first_object.author,
                self.group.slug: first_object.group.slug,
                self.group.title: first_object.group.title,
                self.group.description: first_object.group.description,
            }
            for reverse_name, response_name in objects.items():
                with self.subTest(reverse_name=reverse_name):
                    self.assertEqual(response_name, reverse_name)
        else:
            return AttributeError('На странице нет постов')

    def context_for_all_without_page_obj(self, response):
        if Post.objects.count() >= 1:
            objects = {
                self.post.text: response.context.get('post').text,
                self.post.id: response.context.get('post').id,
                self.user: response.context.get('post').author,
                self.group: response.context.get('post').group,
                self.post: response.context['post'],
            }
            for reverse_name, response_name in objects.items():
                with self.subTest(reverse_name=reverse_name):
                    self.assertEqual(response_name, reverse_name)
        else:
            return AttributeError('На странице нет постов')

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        PostPagesTests.context_for_all_with_page_obj(self, response)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={
                    'slug': PostPagesTests.group.slug
                }
            )
        )
        PostPagesTests.context_for_all_with_page_obj(self, response)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={
                    'username': PostPagesTests.user.username
                }
            )
        )
        PostPagesTests.context_for_all_with_page_obj(self, response)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail', kwargs={
                    'post_id': PostPagesTests.post.id
                }
            )
        )
        PostPagesTests.context_for_all_without_page_obj(self, response)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit', kwargs={
                    'post_id': self.post.id
                }
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        PostPagesTests.context_for_all_without_page_obj(self, response)
        self.assertEqual(response.context['is_edit'], True)

    def test_post_create_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='Fagot',
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок2',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        cls.post = [Post(
            text=f'Тестовый текст {post}',
            group=cls.group,
            author=cls.user,)
            for post in range(13)
        ]
        Post.objects.bulk_create(cls.post)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_first_page_contains_ten_records(self):
        """
        В шаблонах index, group_list и profile на первой странице
        отображается 10 постов, на второй странице - 3 поста.
        """
        field_paginator = {
            self.authorized_client.get(reverse('posts:index')): POSTS_PER_PAGE,
            self.authorized_client.get(
                reverse(
                    'posts:group_list', kwargs={
                        'slug': self.group.slug
                    }
                )
            ): POSTS_PER_PAGE,
            self.authorized_client.get(
                reverse(
                    'posts:profile', kwargs={
                        'username': self.user.username
                    }
                )
            ): POSTS_PER_PAGE,
            self.client.get(reverse('posts:index') + '?page=2'): 3,
            self.authorized_client.get(
                reverse(
                    'posts:group_list', kwargs={
                        'slug': self.group.slug
                    }
                ) + '?page=2'
            ): 3,
            self.authorized_client.get(
                reverse(
                    'posts:profile', kwargs={
                        'username': PaginatorViewsTest.user.username
                    }
                ) + '?page=2'
            ): 3,
        }
        for response, expected_value in field_paginator.items():
            with self.subTest(response=response):
                self.assertEqual(
                    len(response.context['page_obj']), expected_value
                )


class CreatingPostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='Gella',
        )
        cls.group = Group.objects.create(
            title='Группа с постом',
            slug='with',
            description='Группа, в которой появился пост',
        )
        cls.group_1 = Group.objects.create(
            title='Группа без поста',
            slug='without',
            description='Группа, в которой никакого поста не появилось',
        )
        cls.post = Post.objects.create(
            text='Мистер тестовый постик',
            author=cls.user,
            pub_date='05.05.2022',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """"
        Проверяем, что пост появился на
        страницах index, group_list и profile.
        """
        page_names = {
            reverse('posts:index'),
            reverse(
                'posts:group_list', kwargs={
                    'slug': CreatingPostTests.group.slug
                }
            ),
            reverse(
                'posts:profile', kwargs={
                    'username': CreatingPostTests.user.username
                }
            ),
        }
        for page in page_names:
            with self.subTest():
                response = self.authorized_client.get(page)
                post_1 = response.context['page_obj'][0]
                self.assertEqual(response.context['page_obj'][0], 1)
                self.assertEqual(post_1.group.title, 'Группа с постом')

    def test_post_create(self):
        """"Проверяем, что новый пост не попал в другую группу."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={
                    'slug': CreatingPostTests.group_1.slug
                }
            ),
        )
        self.assertEqual(response.context.get('page_obj').paginator.count, 0)
