from django.test import TestCase
from ingredients.models import Ingredient, MeasurementUnit


class MeasurementUnitModelsTest(TestCase):
    '''
    Тестируем модель MeasurementUnit.
    '''
    @classmethod
    def setUpClass(cls):
        '''
        Создаём 1 экземпляр модели MeasurementUnit.
        '''
        super().setUpClass()
        cls.m_u = MeasurementUnit.objects.create(
            name='Mu1',
        )

    def test_ingredients_models_m_u_have_correct_object_names(self):
        """
        Проверяем, что у модели MeasurementUnit корректно работает __str__.
        """
        m_u: MeasurementUnit = MeasurementUnitModelsTest.m_u
        self.assertEqual(
            str(m_u),
            'Размерность: Mu1',
            'Тест не пройден, __str__ MeasurementUnit выводит не ожидаемое')

    def test_ingredients_models_m_u_have_correct_verbose_name(self):
        '''
        Пробежимся по полям модели MeasurementUnit и проверим verbose_name.
        '''
        field_verboses = {
            'name': 'Название',
        }
        m_u: MeasurementUnit = MeasurementUnitModelsTest.m_u
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    m_u._meta.get_field(field).verbose_name,
                    expected_value, (
                        'Тест не пройден, '
                        f'{m_u._meta.get_field(field).verbose_name} '
                        f'вместо {expected_value}'
                    )
                )

    def test_ingredients_models_m_u_have_correct_help_text(self):
        '''
        Пробежимся по полям модели MeasurementUnit и проверим help_text.
        '''
        field_help_text = {
            'name': 'Название',
        }
        m_u: MeasurementUnit = MeasurementUnitModelsTest.m_u
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    m_u._meta.get_field(field).help_text,
                    expected_value,
                    (
                        'Тест не пройден, '
                        f'{m_u._meta.get_field(field).help_text} '
                        f'вместо {expected_value}'
                    )
                )

    def test_ingredients_models_m_u_have_correct_max_length(self):
        '''
        Пробежимся по полям модели MeasurementUnit и проверим max_length.
        '''
        field_max_length = {
            'name': 200,
        }
        m_u: MeasurementUnit = MeasurementUnitModelsTest.m_u
        for field, expected_value in field_max_length.items():
            with self.subTest(field=field):
                self.assertEqual(
                    m_u._meta.get_field(field).max_length,
                    expected_value,
                    (
                        'Тест не пройден, '
                        f'{m_u._meta.get_field(field).max_length} '
                        f'вместо {expected_value}'
                    )
                )

    def test_ingredients_models_m_u_have_correct_unique(self):
        '''
        Пробежимся по полям модели MeasurementUnit и проверим unique.
        '''
        field_unique = {
            'name': True,
        }
        m_u: MeasurementUnit = MeasurementUnitModelsTest.m_u
        for field, expected_value in field_unique.items():
            with self.subTest(field=field):
                self.assertEqual(
                    m_u._meta.get_field(field).unique,
                    expected_value,
                    (
                        'Тест не пройден, '
                        f'{m_u._meta.get_field(field).unique} '
                        f'вместо {expected_value}'
                    )
                )


class IngredientModelsTest(TestCase):
    '''
    Тестируем модель Ingredient.
    '''
    @classmethod
    def setUpClass(cls):
        '''
        Создаём 1 экземпляр модели Ingredient.
        '''
        super().setUpClass()
        cls.m_u = MeasurementUnit.objects.create(
            name='Mu1',
        )
        cls.ingrid = Ingredient.objects.create(
            name='ingrid_1', measurement_unit=cls.m_u
        )

    def test_ingredients_models_ingredient_have_correct_object_names(self):
        """
        Проверяем, что у модели Ingredient корректно работает __str__.
        """
        ingrid: Ingredient = IngredientModelsTest.ingrid
        self.assertEqual(
            str(ingrid),
            'Ингридиент: ingrid_1',
            'Тест не пройден, __str__ Ingredient выводит не ожидаемое')

    def test_ingredients_models_ingredient_have_correct_verbose_name(self):
        '''
        Пробежимся по полям модели Ingredient и проверим verbose_name.
        '''
        field_verboses = {
            'name': 'Название',
            'measurement_unit': 'Размерность',
        }
        ingrid: Ingredient = IngredientModelsTest.ingrid
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    ingrid._meta.get_field(field).verbose_name,
                    expected_value, (
                        'Тест не пройден, '
                        f'{ingrid._meta.get_field(field).verbose_name} '
                        f'вместо {expected_value}'
                    )
                )

    def test_ingredients_models_ingredient_have_correct_help_text(self):
        '''
        Пробежимся по полям модели Ingredient и проверим help_text.
        '''
        field_help_text = {
            'name': 'Название',
            'measurement_unit': 'Размерность',
        }
        ingrid: Ingredient = IngredientModelsTest.ingrid
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    ingrid._meta.get_field(field).help_text,
                    expected_value,
                    (
                        'Тест не пройден, '
                        f'{ingrid._meta.get_field(field).help_text} '
                        f'вместо {expected_value}'
                    )
                )

    def test_ingredients_models_ingredient_have_correct_max_length(self):
        '''
        Пробежимся по полям модели Ingredient и проверим max_length.
        '''
        field_max_length = {
            'name': 200,
        }
        ingrid: Ingredient = IngredientModelsTest.ingrid
        for field, expected_value in field_max_length.items():
            with self.subTest(field=field):
                self.assertEqual(
                    ingrid._meta.get_field(field).max_length,
                    expected_value,
                    (
                        'Тест не пройден, '
                        f'{ingrid._meta.get_field(field).max_length} '
                        f'вместо {expected_value}'
                    )
                )

    def test_ingredients_models_ingredient_have_correct_db_index(self):
        '''
        Пробежимся по полям модели Ingredient и проверим db_index.
        '''
        field_unique = {
            'measurement_unit': True,
        }
        ingrid: Ingredient = IngredientModelsTest.ingrid
        for field, expected_value in field_unique.items():
            with self.subTest(field=field):
                self.assertEqual(
                    ingrid._meta.get_field(field).db_index,
                    expected_value,
                    (
                        'Тест не пройден, '
                        f'{ingrid._meta.get_field(field).db_index} '
                        f'вместо {expected_value}'
                    )
                )
