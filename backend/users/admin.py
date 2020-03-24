from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _
from .models import Profile
from .forms import ProfileCreationForm, ProfileChangeForm
# Register your models here.

class ProfileAdmin(UserAdmin):
    add_form = ProfileCreationForm
    form = ProfileChangeForm
    model = Profile
    # list_display = ['email','username']
    search_fields = ('username', 'first_name', 'profile', )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Extended profile'), {'fields': ('birthday', 'gender','profile')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

# class AddresseAdmin(admin.ModelAdmin):
admin.site.register(Profile, ProfileAdmin)