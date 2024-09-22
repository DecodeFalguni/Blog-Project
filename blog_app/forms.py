from django import forms
from .models import CreateBlog

class CreateBlogForm(forms.ModelForm):
    class Meta:
        model = CreateBlog
        fields = ['title','image','content']

class BlogForm(forms.ModelForm):
    class Meta:
        model = CreateBlog
        fields = ['title', 'image', 'content']
