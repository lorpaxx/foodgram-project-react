# Generated by Django 2.2.20 on 2022-05-20 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20220520_1712'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.CheckConstraint(check=models.Q(cooking_time__gt=0), name='cooking_time_gt_zero'),
        ),
    ]
