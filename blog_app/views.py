from django.shortcuts import render,get_object_or_404
from .forms import CreateBlogForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import BlogForm 
from .models import CreateBlog,Comment
    
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import CreateBlog
from django.core.mail import send_mail
from django.conf import settings

@login_required
def create_blog_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        images = request.FILES.getlist('image')
        
        # Create a new CreateBlog object for each image
        for image in images:
            CreateBlog.objects.create(title=title, image=image, content=content,author=request.user)
            
            mail_subject = 'You posted a new blog!'
            message = f'Hi! {request.user.first_name}, You have posted a new blog: {title}'
            send_mail(mail_subject,message,settings.EMAIL_HOST_USER,[request.user.username])
            
        return redirect('blogs')
    
    return render(request, 'blog_app/create_blog.html')

@login_required
def blog_view(request):
    blogs = CreateBlog.objects.all()
    return render(request, 'blog_app/blogs.html', {'blogs': blogs})

@login_required
def blog_detail_view(request,id):
    blogs = CreateBlog.objects.get(id=id)
    return render(request, 'blog_app/blog_detail.html', {'blogs':blogs})
    
@login_required
def blog_edit_view(request, id):
    blog = get_object_or_404(CreateBlog, id=id)

    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('blog-detail', id=blog.id)
    else:
        form = BlogForm(instance=blog)

    return render(request, 'blog_app/edit_blog.html', {'form': form, 'blog': blog})


@login_required
def blog_delete_view(request, id):
    blog = get_object_or_404(CreateBlog, id=id)

    if request.method == 'POST':
        blog.delete()
        return redirect('blogs')  # Redirect to your blog list page or dashboard

    return render(request, 'blog_app/blog_confirm_delete.html', {'blog': blog})

@login_required
def like_blog(request, blog_id):
    blog = get_object_or_404(CreateBlog, id=blog_id)
    if request.user in blog.likes.all():
        blog.likes.remove(request.user)
    else:
        blog.likes.add(request.user)
        
        if request.user != blog.author:
            mail_subject = 'Your blog received a new like!'
            message = f'Hi! {request.user.first_name}, Your blog: {blog.title} received a new like!'
            send_mail(mail_subject,message,settings.EMAIL_HOST_USER,[blog.author.username])
    
    # Redirect with the correct keyword 'id'
    return redirect('blogs')


# View to add a comment to a blog
@login_required
def add_comment(request, blog_id):
    if request.method == 'POST':
        blog = get_object_or_404(CreateBlog, id=blog_id)
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        parent = Comment.objects.get(id=parent_id) if parent_id else None
        Comment.objects.create(blog=blog, user=request.user, content=content, parent=parent)
        
        if request.user != blog.author:
            mail_subject = 'Your blog received a new comment!'
            message = f'Hi! {request.user.first_name}, Your blog: {blog.title} received a new comment!'
            send_mail(mail_subject,message,settings.EMAIL_HOST_USER,[blog.author.username])
        
    return redirect('blogs')

# View to like/unlike a comment
@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
    return redirect('blogs')

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Ensure the user is allowed to delete this comment
    if request.user == comment.user or request.user.is_superuser:
        comment.delete()
    
    # Redirect back to the blog detail view
    return redirect('blogs')



