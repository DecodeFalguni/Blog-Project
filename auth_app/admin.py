from django.contrib import admin
from .models import CustomUser,UserProfile

@admin.register(CustomUser)
class CustomUser(admin.ModelAdmin):
    class Meta:
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2']
        
@admin.register(UserProfile)
class UserProfile(admin.ModelAdmin):
    class Meta:
        fields = '__all__'   
