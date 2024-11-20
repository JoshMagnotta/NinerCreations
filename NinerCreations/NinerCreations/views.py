# views.py
import re
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Post, Comment
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Post, Activity, Project
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

from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.core.exceptions import ValidationError


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
    topic_id = request.GET.get('topic')

    # Validate topic_id to ensure it's an integer
    if topic_id:
        try:
            topic_id = int(topic_id)
        except ValueError:
            # If topic_id is not a valid integer, return the custom error page
            return render(request, '400.html', status=400)

    # If a valid topic_id is provided, filter by topic, else show all posts
    posts = Post.objects.filter(topics__id=topic_id).order_by('-created_at') if topic_id else Post.objects.all().order_by('-created_at')

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
    projects = Project.objects.filter(user=user)
    
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
        'projects': projects,
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
    # Fetch the completed projects for this user
    projects = Project.objects.filter(user=user).order_by('-created_at')  # Adjust ordering if needed

    # Pass data to the template
    context = {
        'user': user,
        'recent_rooms': recent_rooms,
        'recent_activities': recent_activities,
        'projects': projects,
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

def handle_invalid_topic_id(request, exception):
    # Render the custom 400 error page
    return render(request, '400.html', status=400)

def is_valid_url(url):
    # General URL validation regex
    url_pattern = re.compile(
        r'^(https?:\/\/)?'  # http:// or https://
        r'([a-zA-Z0-9\-_]+\.)+[a-zA-Z]{2,}'  # Domain name
        r'(:\d+)?(\/.*)?$'  # Optional port and path
    )
    return bool(url_pattern.match(url))

def add_project(request):
    if request.method == 'POST':
        name = request.POST.get('project_name')
        description = request.POST.get('project_description')
        link = request.POST.get('project_link')

        # Validate URL
        if not is_valid_url(link):
            messages.error(request, "Please provide a valid URL.")
            return redirect('profile')  # Redirect back to profile with an error message

        # Save the project to the database
        Project.objects.create(user=request.user, name=name, description=description, github_link=link)
        messages.success(request, "Project added successfully!")
        return redirect('profile')

    return render(request, 'profile.html')

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Check if the project belongs to the logged-in user
    if project.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this project.")
    
    project.delete()
    return redirect('profile')  # Redirect back to the profile page

@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Ensure only the owner can edit the project
    if project.user != request.user:
        return HttpResponseForbidden("You are not allowed to edit this project.")

    if request.method == 'POST':
        name = request.POST.get('project_name')
        description = request.POST.get('project_description')
        link = request.POST.get('project_link')

        # Validate URL
        if not is_valid_url(link):
            messages.error(request, "Please provide a valid URL.")
            return redirect('profile')  # Redirect back to profile with an error message

        # Update project details
        project.name = name
        project.description = description
        project.github_link = link
        project.save()

        messages.success(request, "Project updated successfully!")
        return redirect('profile')

    # Render an edit form if method is GET
    context = {'project': project}
    return render(request, 'base/edit_project.html', context)

