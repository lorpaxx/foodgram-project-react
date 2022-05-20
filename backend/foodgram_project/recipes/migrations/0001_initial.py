# Generated by Django 2.2.20 on 2022-05-20 14:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tags', '0001_initial'),
        ('ingredients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название', max_length=200, verbose_name='Название')),
                ('text', models.TextField(help_text='Описание', verbose_name='Описание')),
                ('cooking_time', models.IntegerField(help_text='Время приготовления (в минутах)', verbose_name='Время приготовления (в минутах)')),
                ('image', models.ImageField(upload_to='recipes/', verbose_name='Картинка, закодированная в Base64')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='RecipeTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(help_text='Рецепт', on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe', verbose_name='Рецепт')),
                ('tag', models.ForeignKey(help_text='Тег', on_delete=django.db.models.deletion.CASCADE, to='tags.Tag', verbose_name='Тег')),
            ],
            options={
                'verbose_name': 'Тег рецепта',
                'verbose_name_plural': 'Теги рецептов',
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredientAmount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(help_text='Количество', verbose_name='Количество')),
                ('ingredient', models.ForeignKey(help_text='Ингридиент', on_delete=django.db.models.deletion.CASCADE, to='ingredients.Ingredient', verbose_name='Ингридиент')),
                ('recipe', models.ForeignKey(help_text='Рецепт', on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'Ингридиент рецепта',
                'verbose_name_plural': 'Ингридиенты рецептов',
            },
        ),
    ]
