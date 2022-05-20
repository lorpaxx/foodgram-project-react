from django.contrib.auth import get_user_model
from django.db import models
from ingredients.models import Ingredient
from tags.models import Tag

User = get_user_model()


class Recipe(models.Model):
    '''
    Класс для описания рецептов.
    '''
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text='Автор',
        related_name='recipes',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название',
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Описание',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления (в минутах)',
        help_text='Время приготовления (в минутах)',
    )
    image = models.ImageField(
        'Картинка, закодированная в Base64',
        upload_to='recipes/',
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Тег',
        help_text='Тег'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredientAmount',
        verbose_name='Список ингредиентов',
        help_text='Список ингредиентов'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)
        constraints = (
            models.CheckConstraint(
                check=models.Q(cooking_time__gt=0),
                name='cooking_time_gt_zero'
            ),
        )

    def __str__(self) -> str:
        return f'Рецепт: {self.name} пользователя {self.author}'

    def __repr__(self) -> str:
        return f'Рецепт: {self.name} пользователя {self.author}'


class RecipeTag(models.Model):
    '''
    Класс Recipe_Tag.
    '''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Рецепт',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег',
        help_text='Тег',
        db_index=True,
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'tag'),
                name='unigue_tag_for_recipe'
            ),
        )

    def __str__(self) -> str:
        return f'{self.recipe}, {self.tag}'

    def __repr__(self) -> str:
        return f'{self.recipe}, {self.tag}'


class RecipeIngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент',
        help_text='Ингридиент',
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        help_text='Количество',
    )

    class Meta:
        verbose_name = 'Ингридиент рецепта'
        verbose_name_plural = 'Ингридиенты рецептов'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unigue_ingredient_for_recipe'
            ),
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name='amount_gt_zero'
            )
        )

    def __str__(self) -> str:
        return f'{self.recipe}, {self.ingredient}'

    def __repr__(self) -> str:
        return f'{self.recipe}, {self.ingredient}'
