from django.contrib import admin
from ingredients.models import Ingredient, MeasurementUnit


class MeasurementUnitAdmin(admin.ModelAdmin):
    '''
    Класс MeasurementUnitAdmin.
    '''
    list_display = (
        'pk',
        'name',
    )
    list_editable = ('name',)
    search_fields = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    '''Класс IngredientAdmin.'''
    list_display = (
        'pk',
        'name',
        'measurement_unit'
    )
    list_editable = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit', )
    empty_value_display = '-пусто-'


admin.site.register(MeasurementUnit, MeasurementUnitAdmin)
admin.site.register(Ingredient, IngredientAdmin)
