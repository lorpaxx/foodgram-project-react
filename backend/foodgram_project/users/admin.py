from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import SubscribeUser, User


class SubscribeUserAdmin(admin.ModelAdmin):
    '''
    Класс SubscribeUserAdmin.
    '''
    list_display = (
        'pk',
        'user',
        'author',
    )
    list_editable = (
        'user',
        'author',
    )
    search_fields = ('user__username', 'author__username')


admin.site.register(User, UserAdmin)
admin.site.register(SubscribeUser, SubscribeUserAdmin)
