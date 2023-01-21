from django.test import TestCase, Client

from django.contrib.auth import get_user_model

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
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
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_post_group_url_exists_at_desired_location(self):
        """Страница /group/test-slug/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_profile_url_exists_at_desired_location(self):
        """Страница /profile/HasNoName/ доступна любому пользователю."""
        response = self.guest_client.get('/profile/HasNoName/')
        self.assertEqual(response.status_code, 200)

    def test_post_detail_url_exists_at_desired_location_authorized(self):
        """Страница /posts/1/ доступна любому
        пользователю."""
        response = self.guest_client.get('/posts/1/')
        self.assertEqual(response.status_code, 200)

    def test_post_create_url_exists_at_desired_location_authorized(self):
        """Страница /create/ доступна авторизованному
        пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_exists_at_desired_location_authorized(self):
        """Страница /posts/2/edit/ доступна автору"""
        self.user_2 = User.objects.create_user(username='author')
        self.author = Client()
        self.author.force_login(self.user_2)
        Post.objects.create(
            text='Тестовый текст',
            author=self.user_2
        )
        response = self.author.get('/posts/2/edit/')
        self.assertEqual(response.status_code, 200)

    def test_unexisting_page_url_exists_at_desired_location_authorized(self):
        """Страница /unexisting_page/ доступна любому пользователю"""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_edit_template_exists_authorized(self):
        """Страница /posts/2/edit/ использует соответ. шаблон"""
        self.user_2 = User.objects.create_user(username='author')
        self.author = Client()
        self.author.force_login(self.user_2)
        Post.objects.create(
            text='Тестовый текст',
            author=self.user_2
        )
        response = self.author.get('/posts/2/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')
