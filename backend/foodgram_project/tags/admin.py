from django.contrib import admin

from tags.models import Tag


class TagAdmin(admin.ModelAdmin):
    '''
    Класс TagAdmin.
    '''
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    list_editable = (
        'name',
        'color',
        'slug',
    )
    search_fields = ('slug', 'color')


admin.site.register(Tag, TagAdmin)
