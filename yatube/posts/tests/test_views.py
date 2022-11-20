from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


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
            pub_date='05.02.2022',
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

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        text_0 = first_object.text
        author_0 = first_object.author
        group_0 = first_object.group
        self.assertEqual(text_0, 'Тестовый текст')
        self.assertEqual(author_0, PostPagesTests.user)
        self.assertEqual(group_0, PostPagesTests.group)
        self.assertEqual(response.context['page_obj'][0], PostPagesTests.post)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={
                    'slug': PostPagesTests.group.slug
                }
            )
        )
        self.assertEqual(response.context['group'].title, 'Тестовый заголовок')
        self.assertEqual(response.context['group'].slug, 'test-slug')
        self.assertEqual(
            response.context['group'].description, 'Тестовое описание'
        )
        self.assertEqual(response.context['group'], self.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={
                    'username': PostPagesTests.user.username
                }
            )
        )
        self.assertEqual(response.context['author'], PostPagesTests.user)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail', kwargs={
                    'post_id': PostPagesTests.post.id
                }
            )
        )
        self.assertEqual(
            response.context.get('post').author, PostPagesTests.user
        )
        self.assertEqual(response.context.get('post').text, 'Тестовый текст')
        self.assertEqual(
            response.context.get('post').group, PostPagesTests.post.group
        )
        self.assertEqual(response.context['post'], self.post)
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                text='Тестовый текст',
            ).exists())

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit', kwargs={
                    'post_id': PostPagesTests.post.id
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
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context['post'], self.post)

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
    # Здесь создаются фикстуры: клиент и 13 тестовых записей.
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
        cls.post_1 = Post.objects.create(
            text='Тестовый текст 1',
            author=cls.user,
            pub_date='05.02.2022',
            group=cls.group,
        )
        cls.post_2 = Post.objects.create(
            text='Тестовый текст 2',
            author=cls.user,
            pub_date='05.02.2022',
            group=cls.group,
        )
        cls.post_3 = Post.objects.create(
            text='Тестовый текст 3',
            author=cls.user,
            pub_date='05.02.2022',
            group=cls.group,
        )
        cls.post_4 = Post.objects.create(
            text='Тестовый текст 4',
            author=cls.user,
            pub_date='05.02.2022',
            group=cls.group,
        )
        cls.post_5 = Post.objects.create(
            text='Тестовый текст 5',
            author=cls.user,
            pub_date='05.02.2022',
            group=cls.group,
        )
        cls.post_6 = Post.objects.create(
            text='Тестовый текст 6',
            author=cls.user,
            pub_date='05.02.2022',
            group=cls.group,
        )
        cls.post_7 = Post.objects.create(
            text='Тестовый текст 7',
            author=cls.user,
            pub_date='05.02.2022',
            group=cls.group,
        )
        cls.post_8 = Post.objects.create(
            text='Тестовый текст 8',
            author=cls.user,
            pub_date='05.02.2022',
            group=cls.group,
        )
        cls.post_9 = Post.objects.create(
            text='Тестовый текст 9',
            author=cls.user,
            pub_date='05.02.2022',
            group=cls.group,
        )
        cls.post_10 = Post.objects.create(
            text='Тестовый текст 10',
            author=cls.user,
            pub_date='05.02.2022',
            group=cls.group,
        )
        cls.post_11 = Post.objects.create(
            text='Тестовый текст 11',
            author=cls.user,
            pub_date='05.02.2022',
            group=cls.group,
        )
        cls.post_12 = Post.objects.create(
            text='Тестовый текст 12',
            author=cls.user,
            pub_date='05.02.2022',
            group=cls.group,
        )
        cls.post_13 = Post.objects.create(
            text='Тестовый текст 13',
            author=cls.user,
            pub_date='05.02.2022',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_first_page_contains_ten_records(self):
        """На первой странице index отображается 10 постов."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_three_records(self):
        """На второй странице index отображается 3 поста."""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_first_page_contains_ten_records(self):
        """На первой странице group_list отображается 10 постов."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={
                    'slug': PaginatorViewsTest.group.slug
                }
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_second_page_contains_three_records(self):
        """На второй странице group_list отображается 3 поста."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={
                    'slug': PaginatorViewsTest.group.slug
                }
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        """На первой странице profile отображается 10 постов."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={
                    'username': PaginatorViewsTest.user.username
                }
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_three_records(self):
        """На второй странице profile отображается 3 поста."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={
                'username': PaginatorViewsTest.user.username
            }
            ) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


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
                post_1_id = post_1.id
                post_1_group = post_1.group.title
                self.assertEqual(post_1_id, 1)
                self.assertEqual(post_1_group, 'Группа с постом')

    def test_post_create(self):
        """"Проверяем, что новый пост пне попал в другую группу."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={
                    'slug': CreatingPostTests.group_1.slug
                }
            ),
        )
        self.assertEqual(response.context.get('page_obj').paginator.count, 0)
