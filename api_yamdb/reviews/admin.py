from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import User, Genre, Category, Comment, Title, Review


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'bio', 'role', 'is_active', 'confirmation_code'
    )
    list_filter = (
        'username', 'email', 'first_name', 'last_name',
        'bio', 'role', 'is_active', 'confirmation_code'
    )
    fieldsets = (
        (None, {'fields': (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role', 'password'
        )}),
        ('Permissions', {'fields': ('is_active',)}),
    )
    search_fields = ('email', 'username')
    ordering = ('email', 'username')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Genre)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Title)
admin.site.register(Review)
