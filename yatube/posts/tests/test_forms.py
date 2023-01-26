import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import User, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': 'Test'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст'
            ).exists()
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': 'Тестовая группа',
        }
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                group=self.group
            ).exists()
        )

    def test_create_post_by_guest_client(self):
        """Аноним не может создавать посты"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_edit_post_by_guest_client(self):
        """Аноним не может редактировать посты"""
        form_data = {
            'text': 'Тестовый текст',
        }
        self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст'
            ).exists()
        )

    def test_edit_post_by_no_author(self):
        """Не автор не может редактировать посты"""
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                    'post_id': self.post.id}))
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
                                               'post_id': self.post.id}))
