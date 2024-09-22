from django.contrib import admin
from .models import CreateBlog

# Register your models here.
@admin.register(CreateBlog)
class CreateBlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'content')