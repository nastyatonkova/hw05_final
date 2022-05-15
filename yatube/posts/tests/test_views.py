import shutil
import tempfile
from http import HTTPStatus

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

TESTING_ATTEMPTS = 13
OTHER_GROUP_SLUG = 'other-test-group'
OTHER_GROUP_URL = reverse('posts:group_list', args=[OTHER_GROUP_SLUG])


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )
        image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='test.jpg',
            content=image,
            content_type='image/jpg'
        )
        self.post = Post.objects.create(
            text='Test text',
            author=self.user,
            group=self.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-adress uses correct HTML-template."""
        cache.clear()
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': self.group.slug})
            ),
            'posts/profile.html': (
                reverse('posts:profile',
                        kwargs={'username': self.user.username})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': self.post.id})
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_pages_uses_correct_template(self):
        """URL-adress post_edit uses template create_post.html."""
        response = (self.authorized_client.
                    get(reverse('posts:post_edit',
                        kwargs={'post_id': self.post.id})))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_post_show_picture(self):
        """Check the image."""
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): self.post.image,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): self.post.image,
            reverse('posts:profile',
                    kwargs={'username': self.user.username}): self.post.image,
        }
        for value, expected in templates_pages_names.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.image, expected)

    def test_post_show_picture_in_post(self):
        """Check the image on post page."""
        response = (self.authorized_client.
                    get(reverse('posts:post_edit',
                        kwargs={'post_id': self.post.id})))
        post = response.context['required_post']
        self.assertEqual(post.image, self.post.image)

    def test_group_list_page_show_correct_context(self):
        """Template group_list gives group list of the posts."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                        kwargs={'slug': self.group.slug})))
        group = response.context['group']
        self.assertEqual(group, Group.objects.get(slug=self.group.slug))

    def test_profile_page_show_correct_context(self):
        """Template profile gives list of the author's posts."""
        response = (self.authorized_client.
                    get(reverse('posts:profile',
                        kwargs={'username': self.user.username})))
        author = response.context['author']
        posts_count = response.context['posts_count']
        self.assertEqual(author, User.objects.get(username=self.user.username))
        self.assertEqual(posts_count, Post.objects.filter(
            author__username=self.user.username
        ).count())

    def test_post_detail_pages_show_correct_context(self):
        """Template post_detail gives one post filtered by its id."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                        kwargs={'post_id': self.post.id})))
        post = response.context['post']
        posts_count = response.context['posts_count']
        self.assertEqual(post, Post.objects.get(id=self.post.id))
        self.assertEqual(posts_count, 1)

    def test_create_post_show_correct_context(self):
        """Template create_post gives form to create post."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        is_edit = response.context.get('is_edit')
        self.assertEqual(is_edit, False)

    def test_post_edit_pages_show_correct_context(self):
        """Template create_post gives form to edit post."""
        response = (self.authorized_client.
                    get(reverse('posts:post_edit',
                        kwargs={'post_id': self.post.id})))
        required_post = response.context['required_post']
        self.assertEqual(required_post, Post.objects.get(id=self.post.id))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        is_edit = response.context.get('is_edit')
        self.assertEqual(is_edit, True)

    def test_post_show_correct_text(self):
        """Additional check of first post text appering in the right group."""
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): self.post.text,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): self.post.text,
            reverse('posts:profile',
                    kwargs={'username': self.user.username}): self.post.text,
        }
        for value, expected in templates_pages_names.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.text, expected)

    def test_post_show_correct_post_id(self):
        """Checking id of first post and appering in the right group."""
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): self.post.id,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): self.post.id,
            reverse('posts:profile',
                    kwargs={'username': self.user.username}): self.post.id,
        }
        for value, expected in templates_pages_names.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.id, expected)

    def test_new_post_do_not_view_other_group(self):
        """New post will not appear in other group."""
        Group.objects.create(
            title='Другой заголовок',
            slug=OTHER_GROUP_SLUG,
            description='Другое тестовое описание',
        )
        response = self.authorized_client.get(OTHER_GROUP_URL)
        self.assertNotIn(self.post, response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.user = User.objects.create_user(username='TestUser2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Test group_2',
            slug='test-slug_2',
            description='Test description_2',
        )
        self.post = Post.objects.bulk_create(
            [
                Post(
                    text='Testing paginator',
                    author=self.user,
                    group=self.group,
                ),
            ] * TESTING_ATTEMPTS
        )

    def test_first_page_contains_ten_records(self):
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): settings.POSTS_IN_PAGINATOR,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}):
            settings.POSTS_IN_PAGINATOR,
            reverse('posts:profile',
                    kwargs={'username': self.user.username}):
            settings.POSTS_IN_PAGINATOR,
        }
        for reverse_template, expected in templates_pages_names.items():
            with self.subTest(reverse_template=reverse_template):
                response = self.client.get(reverse_template)
                self.assertEqual(len(response.context['page_obj']), expected)

    def test_second_page_contains_three_records(self):
        all_posts = Post.objects.filter(
            author__username=self.user.username
        ).count()
        second_page_posts = all_posts - settings.POSTS_IN_PAGINATOR
        templates_pages_names = {
            reverse('posts:index'): second_page_posts,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): second_page_posts,
            reverse('posts:profile',
                    kwargs={'username': self.user.username}):
            second_page_posts,
        }
        for reverse_template, expected in templates_pages_names.items():
            with self.subTest(reverse_template=reverse_template):
                response = self.client.get(reverse_template + '?page=2')
                self.assertEqual(len(response.context['page_obj']), expected)


class FollowViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
        )

    def setUp(self):
        self.user = User.objects.create_user(username='authFollower')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_autorized_user_can_follow(self):
        """User can follow authors."""
        follow_count = Follow.objects.count()
        author = FollowViewsTests.user
        response = (self.authorized_client.
                    get(reverse('posts:profile_follow',
                        kwargs={'username': author.username})))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=author
        ).exists())

    def test_autorized_user_can_unfollow(self):
        """User can unfollow authors."""
        author = FollowViewsTests.user
        Follow.objects.create(user=self.user, author=author)
        follow_count = Follow.objects.count()
        response = (self.authorized_client.
                    get(reverse('posts:profile_unfollow',
                        kwargs={'username': author.username})))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), follow_count - 1)
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=author
        ).exists())

    def test_autorized_user_can_follow_once(self):
        """User can follow author only once."""
        follow_count = Follow.objects.count()
        author = FollowViewsTests.user
        response = (self.authorized_client.
                    get(reverse('posts:profile_follow',
                        kwargs={'username': author.username})))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=author
        ).exists())
        follow_count = Follow.objects.count()
        response = (self.authorized_client.
                    get(reverse('posts:profile_follow',
                        kwargs={'username': author.username})))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), follow_count)
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=author
        ).exists())

    def test_autorized_user_cant_follow_yourself(self):
        """User cannot follow himself."""
        follow_count = Follow.objects.count()
        response = (self.authorized_client.
                    get(reverse('posts:profile_follow',
                        kwargs={'username': self.user.username})))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), follow_count)
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=self.user
        ).exists())

    def test_follow_index(self):
        """Checking the page of following authors."""
        author = FollowViewsTests.user
        self.authorized_client.get(reverse('posts:profile_follow',
                                   kwargs={'username': author.username}))
        response = (self.authorized_client.get(reverse('posts:follow_index')))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.id, self.post.id)
        self.authorized_client.get(reverse('posts:profile_unfollow',
                                   kwargs={'username': author.username}))
        response = (self.authorized_client.get(reverse('posts:follow_index')))
        self.assertNotContains(response, self.post.text)
