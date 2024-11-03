from .models import Post, Comment
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        content = request.POST.get('content')  # Get the comment content from the form

        if content:
            author = request.user if request.user.is_authenticated else None

            Comment.objects.create(
                post=post,
                author=author,
                content=content
            )
            # Render the post detail page with the new comment
            return render(request, 'base/post_detail.html', {
                'post': post,
                'success_message': "Comment added successfully!"  # Pass a success message to the template
            })

    # If not a POST request or if comment was not added, render the post detail page
    return render(request, 'base/post_detail.html', {
        'post': post,
        'error_message': "Failed to add comment."  # Pass an error message to the template
    })

# @login_required
def recent_activity_view(request):
    # Query for the 10 most recent posts and comments
    recent_posts = Post.objects.all().order_by('-created_at')[:10]
    recent_comments = Comment.objects.all().order_by('-created_at')[:10]

    # Combine posts and comments into a single list and sort by created_at
    recent_activities = sorted(
        list(recent_posts) + list(recent_comments),
        key=lambda x: x.created_at,
        reverse=True
    )[:10]  # Get the top 10 most recent activities

    return render(request, 'base/home.html', {
        'recent_activities': recent_activities
    })

def home_view(request):
    # Retrieve all posts ordered by creation date (newest first)
    posts = Post.objects.all().order_by('-created_at')
    
    # Retrieve the 10 most recent posts and comments
    recent_posts = Post.objects.all().order_by('-created_at')[:10]
    recent_comments = Comment.objects.all().order_by('-created_at')[:10]

    # Combine posts and comments, then sort by created_at to get the 10 most recent activities
    recent_activities = sorted(
        list(recent_posts) + list(recent_comments),
        key=lambda x: x.created_at,
        reverse=True
    )[:10]

    # Pass both posts and recent_activities to the template
    return render(request, 'base/home.html', {
        'posts': posts,
        'recent_activities': recent_activities
    })


def home(request):
    return render(request, 'base/home.html')

def profile(request):
    return render(request, 'base/profile.html')

def settings(request):
    return render(request, 'base/settings.html')

def login(request):
    return render(request, 'base/login.html')

