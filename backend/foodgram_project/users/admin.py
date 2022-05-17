from django.contrib import admin
from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'password',
    )
    search_fields = ('username', 'email',)


admin.site.register(User, UserAdmin)
