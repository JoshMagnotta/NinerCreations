from .models import Post, Comment
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, UserProfile, Room, Activity

def post_detail(request, post_id):
    # Retrieve the specific post using the provided post_id
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'base/post_detail.html', {'post': post})

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

def profile_view(request, pk):
    user_profile = get_object_or_404(UserProfile, user__pk=pk)
    recent_rooms = Room.objects.filter(created_by=user_profile.user).order_by('-created_at')[:5]  # Last 5 rooms
    recent_posts = Post.objects.filter(author=user_profile.user).order_by('-created_at')[:10]
    recent_comments = Comment.objects.filter(author=user_profile.user).order_by('-created_at')[:10]
    
    # Combine posts and comments, then sort by created_at to get the 10 most recent activities
    recent_activities = sorted(
        list(recent_posts) + list(recent_comments),
        key=lambda x: x.created_at,
        reverse=True
    )[:10]

    context = {
        'user_profile': user_profile,
        'recent_rooms': recent_rooms,
        'recent_activities': recent_activities,
    }
    return render(request, 'base/profile.html', context)

def create_post(request):
    if request.method == 'POST':
        # Handle post creation
        post = Post.objects.create(
            title=request.POST['title'],
            content=request.POST['content'],
            user=request.user
        )
        
        # Log the activity
        Activity.objects.create(user=request.user, action='CREATED_POST', post=post)
        
        # Redirect or render response
        return redirect('profile', pk=request.user.pk)
    
    return render(request, 'posts/create_post.html')

def home(request):
    return render(request, 'base/home.html')

def profile(request):
    return render(request, 'base/profile.html')

def settings(request):
    return render(request, 'base/settings.html')

def login(request):
    return render(request, 'base/login.html')

