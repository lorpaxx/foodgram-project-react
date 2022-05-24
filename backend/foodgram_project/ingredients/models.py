from django.db import models


class MeasurementUnit(models.Model):
    '''
    Класс для размерностей игридиентов.
    '''
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название',
        unique=True,
    )

    class Meta:
        verbose_name = 'Размерность'
        verbose_name_plural = 'Размерности'
        ordering = ('name',)

    def __str__(self):
        return f'Размерность: {self.name}'

    def __repr__(self):
        return f'Размерность: {self.name}'


class Ingredient(models.Model):
    '''
    Модель для ингридиентов.
    '''
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название',
    )
    measurement_unit = models.ForeignKey(
        MeasurementUnit,
        on_delete=models.CASCADE,
        null=True,
        related_name='ingredients',
        verbose_name='Размерность',
        help_text='Размерность',
        db_index=True,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'Ингридиент: {self.name}'

    def __repr__(self) -> str:
        return f'Ингридиент: {self.name}'
