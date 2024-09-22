from django.db import models
from auth_app.models import CustomUser

# Create your models here.

class CreateBlog(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='blog_images/')
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blogs', default=1)  # Link to the user who created the blog
    likes = models.ManyToManyField(CustomUser, related_name='blog_likes', blank=True)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title
    
    
class Comment(models.Model):
    blog = models.ForeignKey(CreateBlog, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(CustomUser, related_name='comment_likes', blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"Comment by {self.user.username} on {self.blog.title}"