# Generated by Django 2.2.20 on 2022-06-03 13:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_auto_20220601_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(help_text='Время приготовления (в минутах)', validators=[django.core.validators.MinValueValidator(limit_value=1)], verbose_name='Время приготовления (в минутах)'),
        ),
        migrations.AlterField(
            model_name='recipeingredientamount',
            name='amount',
            field=models.PositiveSmallIntegerField(help_text='Количество', validators=[django.core.validators.MinValueValidator(limit_value=1)], verbose_name='Количество'),
        ),
    ]
