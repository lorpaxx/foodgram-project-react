# Generated by Django 2.2.20 on 2022-05-31 16:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20220526_2009'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscribeuser',
            options={'verbose_name': 'Подписка пользователя', 'verbose_name_plural': 'Подписки пользователя'},
        ),
    ]
