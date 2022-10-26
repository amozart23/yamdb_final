import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from rest_framework_simplejwt.tokens import AccessToken

from .enums import Role
from .validators import validate_year


class User(AbstractUser):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=9,
        choices=[(role.value, role.value) for role in Role],
        blank=True,
        null=True,
        default=Role.USER
    )
    confirmation_code = models.CharField(max_length=256, default=uuid.uuid4)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.email

    @property
    def token(self):
        return AccessToken.for_user(self)

    @property
    def is_admin(self):
        return self.role == Role.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return (
            self.role == Role.MODERATOR
            or self.role == Role.ADMIN
            or self.is_superuser
        )

    @property
    def is_user(self):
        return self.role == Role.USER


class Category(models.Model):
    name = models.TextField('Категория', max_length=150)
    slug = models.SlugField('slug', unique=True, db_index=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'category'

    def __str__(self):
        return self.name[:10]


class Genre(models.Model):
    name = models.TextField('Жанр', max_length=150)
    slug = models.SlugField('slug', unique=True, db_index=True)

    class Meta:
        verbose_name = 'genre'
        verbose_name_plural = 'genre'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.TextField(
        'Произведение',
        blank=False,
        max_length=200,
        db_index=True
    )
    year = models.IntegerField('Год', blank=True, validators=[validate_year])
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles',
        verbose_name='категория'
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        db_index=True,
        related_name='titles',
        verbose_name='жанр'
    )
    description = models.CharField(
        'описание',
        max_length=200,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'title'
        verbose_name_plural = 'title'

    def __str__(self):
        return self.name[:10]


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(
        'Отзыв',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='автор'
    )
    score = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1), MaxValueValidator(10)),
        error_messages={'validators': 'Оценка от 1 до 10.'}
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_author_review'
            )
        ]
        verbose_name = 'review'
        verbose_name_plural = 'review'


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='отзыв'
    )
    text = models.TextField(
        'Комментарий',
        max_length=300
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'comment'
        verbose_name_plural = 'comment'
