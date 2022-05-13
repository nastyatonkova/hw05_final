from django.contrib.auth import get_user_model
from django.db import models

from posts.validators import validate_not_empty

User = get_user_model()


class Group(models.Model):
    """Class for creating groups."""
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=200,
        help_text='Дайте название группы'
    )
    slug = models.SlugField(
        verbose_name='Slug',
        unique=True,
        help_text='Дайте ключ адреса страницы'
    )
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Опишите группу'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    """Class for creating posts."""
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста',
        validators=[validate_not_empty])
    pub_date = models.DateTimeField(
        verbose_name='date published',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        related_name='posts',
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    """Class for commenting posts."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    created = models.DateTimeField(
        'date published',
        auto_now_add=True
    )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-created']


class Follow(models.Model):
    """Class to follow authors."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_follow')
        ]
