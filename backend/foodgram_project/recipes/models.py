from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from foodgram_project.settings import PROJECT_SETTINGS
from ingredients.models import Ingredient
from tags.models import Tag

User = get_user_model()


class Recipe(models.Model):
    '''
    Класс Recipe для описания рецептов.
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
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        help_text='Время приготовления (в минутах)',
        validators=(
            MinValueValidator(
                limit_value=PROJECT_SETTINGS.get('recipes_min_cooking_time', 1)
            ),
        )
    )
    image = models.ImageField(
        'Картинка',
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

    def __str__(self) -> str:
        return f'Рецепт: {self.name}'

    def __repr__(self) -> str:
        return f'Рецепт: {self.name}'


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
    '''
    Класс RecipeIngredientAmount.
    '''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Рецепт',
        db_index=True,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент',
        help_text='Ингридиент',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        help_text='Количество',
        validators=(
            MinValueValidator(
                limit_value=PROJECT_SETTINGS.get('ingredient_min_amount', 1)
            ),
        )
    )

    class Meta:
        verbose_name = 'Ингридиент рецепта'
        verbose_name_plural = 'Ингридиенты рецептов'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unigue_ingredient_for_recipe'
            ),
        )

    def __str__(self) -> str:
        return f'{self.recipe}, {self.ingredient}'

    def __repr__(self) -> str:
        return f'{self.recipe}, {self.ingredient}'


class UserFavoriteRecipe(models.Model):
    '''
    Класс UserFavoriteRecipe.
    '''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='favorite_recipes',
        verbose_name='Пользователь',
        help_text='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='in_favorite',
        verbose_name='Рецепт',
        help_text='Рецепт'
    )

    class Meta:
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unigue_recipe_user_favorite'
            ),
        )


class UserShoppingCart(models.Model):
    '''
    Класс UserShoppingCart.
    '''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='shopping_recipes',
        verbose_name='Пользователь',
        help_text='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='in_shopping',
        verbose_name='Рецепт',
        help_text='Рецепт'
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unigue_recipe_user_shoping'
            ),
        )
