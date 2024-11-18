# views.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Post, Comment
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Post, Activity
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.shortcuts import render, redirect
from django.contrib import messages
from .registerform import RegisterForm
from .models import Profile
from .forms import ProfileForm
from .forms import UsernameChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import Post, Comment, Activity, Profile
from .forms import ProfileForm, UsernameChangeForm
from .forms import UpdateEmailForm
from django.shortcuts import redirect
from .forms import ProfileUpdateForm


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('-created_at')  # Fetch comments associated with the post

    if request.method == 'POST':
        content = request.POST.get('content')  # Get the comment content from the form

        if content:
            author = request.user if request.user.is_authenticated else None
            Comment.objects.create(post=post, author=author, content=content)
            # After adding the comment, fetch comments again to include the new one
            comments = post.comments.all().order_by('-created_at')

    # Render the post detail page with the post and comments
    return render(request, 'base/post_detail.html', {
        'post': post,
        'comments': comments,
    })
    
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

# views.py
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment, Topic

# views.py

def home_view(request):
    # Retrieve the topic filter from the URL parameters
    topic_id = request.GET.get('topic')

    if topic_id:
        # Filter posts by the selected topic
        posts = Post.objects.filter(topics__id=topic_id).order_by('-created_at')
    else:
        # If no topic is selected, retrieve all posts
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

    # Retrieve all topics for the "Browse Topics" section
    topics = Topic.objects.all()

    # Pass the posts, recent activities, and topics to the template
    return render(request, 'base/home.html', {
        'posts': posts,
        'recent_activities': recent_activities,
        'topics': topics
    })




@login_required
def profile_view(request):
    user = request.user
    recent_rooms = Post.objects.filter(author=user).order_by('-created_at')[:5]  # Last 5 rooms
    recent_posts = Post.objects.filter(author=user).order_by('-created_at')[:10]
    recent_comments = Comment.objects.filter(author=user).order_by('-created_at')[:10]
    
    # Combine posts and comments, then sort by created_at to get the 10 most recent activities
    recent_activities = sorted(
        list(recent_posts) + list(recent_comments),
        key=lambda x: x.created_at,
        reverse=True
    )[:10]

    context = {
        'user': user,
        'recent_rooms': recent_rooms,
        'recent_activities': recent_activities,
    }
    return render(request, 'base/profile.html', context)


def user_profile_view(request, pk):
    # Get the user object based on the primary key (pk)
    user = get_object_or_404(User, pk=pk)
    
    # Fetch recent rooms, posts, and comments by the user
    recent_rooms = Post.objects.filter(author=user).order_by('-created_at')[:5]  # Last 5 rooms
    recent_posts = Post.objects.filter(author=user).order_by('-created_at')[:10]
    recent_comments = Comment.objects.filter(author=user).order_by('-created_at')[:10]
    
    # Combine posts and comments, then sort by created_at to get the 10 most recent activities
    recent_activities = sorted(
        list(recent_posts) + list(recent_comments),
        key=lambda x: x.created_at,
        reverse=True
    )[:10]

    # Pass data to the template
    context = {
        'user': user,
        'recent_rooms': recent_rooms,
        'recent_activities': recent_activities,
    }
    return render(request, 'base/user_profile.html', context)

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
def search(request):
    query = request.GET.get('q', '')
    if query:
        # Search by title OR description using Q objects
        posts = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
    else:
        posts = Post.objects.none()
    return render(request, 'base/search_results.html', {'posts': posts, 'query': query})

def home(request):
    return render(request, 'base/home.html')

def profile(request):
    return render(request, 'base/profile.html')

def settings(request):
    return render(request, 'base/settings.html')

def login(request):
    return render(request, 'base/login.html')

#Register account stuff
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')  # Redirect to the login page after registration
    else:
        form = RegisterForm()
    return render(request, 'base/register.html', {'form': form})

@login_required
def bio_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'base/bio.html', {'profile': profile})

@login_required
def settings(request):
    # Get the user's profile, or create it if it doesn't exist
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Get updated bio and username from the form
        bio = request.POST.get('bio')
        username = request.POST.get('username')
        
        # Get and validate new password if provided
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Update bio and username
        request.user.username = username
        profile.bio = bio
        profile.save()
        
        # Update password if provided and valid
        if password and password == confirm_password:
            request.user.set_password(password)
            update_session_auth_hash(request, request.user)  # Keep user logged in after password change
            messages.success(request, "Your password was successfully updated!")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('settings')

        # Save user information
        request.user.save()
        messages.success(request, "Your settings were successfully updated.")
        return redirect('settings')
    
    return render(request, 'base/settings.html', {'profile': profile, 'user': request.user})

@login_required
def settings_view(request):
    user = request.user
    if request.method == 'POST':
        email_form = UpdateEmailForm(request.POST, instance=user)
        if email_form.is_valid():
            email_form.save()
            messages.success(request, 'Your email has been updated successfully!')
            return redirect('settings')
        else:
            messages.error(request, 'Please correct the error below.')

    else:
        email_form = UpdateEmailForm(instance=user)

    context = {
        'email_form': email_form,
    }
    return render(request, 'base/settings.html', context)

@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        messages.success(request, "Your account has been successfully deleted.")
        return redirect('home')  # Redirect to home page or any other page
    else:
        messages.error(request, "Invalid request.")
        return redirect('settings')  # Redirect back to settings page
    
@login_required
def settings(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('settings')
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'base/settings.html', {'form': form})