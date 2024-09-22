from django.urls import path
from . import views

urlpatterns = [
    path('create-blog/', views.create_blog_view,name='create-blog'),
    path('blogs/', views.blog_view,name='blogs'),
    path('blog-detail/<int:id>', views.blog_detail_view,name='blog-detail'),
    path('edit-blog/<int:id>', views.blog_edit_view,name='edit-blog'),
    path('delete-blog/<int:id>', views.blog_delete_view,name='delete-blog'),
    path('like/<int:blog_id>/', views.like_blog, name='like-blog'),
    path('comment/<int:blog_id>/', views.add_comment, name='add-comment'),
    path('like-comment/<int:comment_id>/', views.like_comment, name='like-comment'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete-comment'),
    # path('logout/', views.logout_view,name='logout'),
]