from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Добавляем наши поля (бан, аватар) в админку
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('is_banned', 'avatar')}),
    )
    list_display = ('username', 'email', 'is_staff', 'is_banned')
    list_filter = ('is_staff', 'is_superuser', 'is_banned', 'groups')

admin.site.register(CustomUser, CustomUserAdmin)