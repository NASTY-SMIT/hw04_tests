from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Name')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.user = User.objects.create_user(username='Test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            (reverse('posts:group_list', kwargs={'slug': self.group.slug})
             ): 'posts/group_list.html',
            (reverse('posts:profile', kwargs={'username': 'Test'})
             ): 'posts/profile.html',
            (reverse('posts:post_detail', kwargs={'post_id': '1'})
             ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_template_name_exists_authorized(self):
        """URL-адрес /posts/2/edit/ использует соответствующий шаблон."""
        self.user_2 = User.objects.create_user(username='author')
        self.author = Client()
        self.author.force_login(self.user_2)
        Post.objects.create(
            text='Тестовый текст',
            author=self.user_2
        )
        response = self.author.get(
            reverse('posts:post_edit', kwargs={'post_id': '2'}))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        expected = list(
            Post.objects.select_related('author', 'group').order_by(
                '-pub_date'))[:10]
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:group_list',
                    kwargs={'slug': self.group.slug})))
        expected = list(
            Post.objects.filter(group_id=self.group.id).order_by(
                '-pub_date'))[:10]
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:profile',
                    kwargs={'username': self.user})))
        expected = list(
            Post.objects.filter(author_id=self.user.id).order_by(
                '-pub_date'))[:10]
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})))
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').group, self.post.group)

    def test_post_create_pages_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_pages_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        self.user_5 = User.objects.create_user(username='Тестировщик')
        self.author = Client()
        self.author.force_login(self.user_5)
        Post.objects.create(
            text='Тестовый текст',
            author=self.user_5,
            id='7'
        )
        response = self.author.get(reverse(
                                   'posts:post_edit', kwargs={'post_id': '7'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
