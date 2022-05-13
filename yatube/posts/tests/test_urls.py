from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

REDIRECT_LOGIN_CREATE = '/auth/login/?next=/create/'
REDIRECT_LOGIN_EDIT = '/auth/login/?next=/posts/1/edit/'
REDIRECT_POST_DETAIL = '/posts/1/'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.user2 = User.objects.create_user(username='not_auth')
        self.authorized_client = Client()
        self.authorized_client2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2.force_login(self.user2)
        self.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )
        self.post = Post.objects.create(
            text='Test text',
            author=self.user,
            group=self.group
        )

    def test_urls_for_unauthorised_users(self):
        """Pages available for all users."""
        page_url_names = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user.username}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            # Проверьте, что запрос к несуществующей странице вернёт ошибку 404
            '/unexisting_page/': HTTPStatus.NOT_FOUND
        }
        for page, expected_status in page_url_names.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page).status_code
                self.assertEqual(response, expected_status)

    def test_create_url_exists_at_desired_location(self):
        """Page /create/ available for authorised users."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url_exists_at_desired_location(self):
        """Page /edit/ available for author of the post."""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-adress using correct HTML templates."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
            'posts/profile.html': f'/profile/{self.user.username}/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/create_post.html': '/create/',
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_edit_url_uses_correct_template(self):
        """Page /edit/ uses correct HTML create_post template."""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_urls_redirect(self):
        """URL redirects user on right page."""
        client_url_redirect = [
            [self.guest_client, reverse(
                'posts:post_create'), REDIRECT_LOGIN_CREATE],
            [self.guest_client, '/posts/1/edit/', REDIRECT_LOGIN_EDIT],
            [self.authorized_client2, '/posts/1/edit/', REDIRECT_POST_DETAIL]
        ]
        for client, url, redirect_url in client_url_redirect:
            with self.subTest(url=url):
                self.assertRedirects(
                    client.get(url, follow=True), redirect_url)
