from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    '''
    Класс User вместо стандартного.
    '''
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        help_text='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        help_text='Фамилия',
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        help_text='Адрес электронной почты',
        unique=True,
    )
    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        help_text='Уникальный юзернейм',
        max_length=150,
        unique=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
