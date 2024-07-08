from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    email = models.EmailField(
        'email',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=150
    )
    first_name = models.CharField(
        'Имя',
        max_length=150
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['-id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):

    subscriber = models.ForeignKey(
        User,
        related_name='subscriber',
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        related_name='subscribing',
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'user'],
                name='unique_subscription'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
