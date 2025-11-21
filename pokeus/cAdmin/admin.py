from django.contrib import admin
from .models import CustomUser,Priority,Department,Company,Category
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
# Register your models here.


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = '__all__'


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'


# Custom User Admin
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'is_staff','department','company','contact','role']
    list_filter = ['is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('department','company','contact','role')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2','company','contact','role'),
        }),
    )

admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(Priority)
admin.site.register(Company)
# admin.site.register(Department)
# admin.site.register(Category)
admin.site.unregister(Group)





