from django.contrib import admin
from .models import User, UserProfile
from django.contrib.auth.admin import UserAdmin

#used to make Password Read Only
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 
    'username', 'role', 'is_active')  # used to specify the fields to display on Admin page
    ordering = ('-date_joined',) #note u must end a tuple of 1 element with (comma),
    filter_horizontal=()
    list_filter = ()
    fieldsets = ()


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
