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
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.core.exceptions import ValidationError

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

# View to create a new post
def create_post(request):
    # Fetch all topics to display in the form
    topics = Topic.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        topic_ids = request.POST.getlist('topics')  # Get selected topics (multiple)

        # Ensure the user is logged in
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to create a post.")
            return redirect('login')

        if title and content:
            # Create the post
            post = Post.objects.create(
                author=request.user,
                title=title,
                content=content
            )

            # Add selected topics to the post
            post.topics.set(Topic.objects.filter(id__in=topic_ids))

            # Log the creation of the post as an activity
            Activity.objects.create(user=request.user, action='CREATED_POST', post=post)

            messages.success(request, "Post created successfully.")
            return redirect('post_detail', pk=post.pk)

    return render(request, 'base/create_post.html', {'topics': topics})

# View to display a single post and its details (including comments)
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all().order_by('-created_at')  # Fetch comments associated with the post

    # Handle comment submission
    if request.method == 'POST':
        content = request.POST.get('content')  # Get the comment content from the form

        if content:
            author = request.user if request.user.is_authenticated else None
            Comment.objects.create(post=post, author=author, content=content)
            # After adding the comment, fetch comments again to include the new one
            comments = post.comments.all().order_by('-created_at')

        # Handle delete comment for post owner or comment owner
        if 'delete_comment' in request.POST:
            comment_id = request.POST.get('delete_comment')
            comment = get_object_or_404(Comment, pk=comment_id)
            
            # Ensure only the post owner or the comment owner can delete it
            if request.user == post.author or request.user == comment.author:
                comment.delete()
                messages.success(request, "Comment deleted successfully.")
            else:
                messages.error(request, "You do not have permission to delete this comment.")
        
            return redirect('post_detail', pk=pk)

        # Handle Join or Leave post
        if 'join' in request.POST:
            # Check if the user is already a member of the post
            if request.user not in post.members.all():
                post.members.add(request.user)
                # Remove the old "JOINED_POST" activity if it exists
                Activity.objects.filter(post=post, user=request.user, action='JOINED_POST').delete()
                # Log the new "JOINED_POST" action with the current timestamp
                Activity.objects.create(user=request.user, action='JOINED_POST', post=post)
                messages.success(request, "You have joined the group.")
            else:
                messages.info(request, "You are already a member of this post.")
                
        elif 'leave' in request.POST:
            # Check if the user is a member before allowing them to leave
            if request.user in post.members.all():
                post.members.remove(request.user)
                # Remove the old "LEFT_POST" activity if it exists
                Activity.objects.filter(post=post, user=request.user, action='LEFT_POST').delete()
                # Log the new "LEFT_POST" action with the current timestamp
                Activity.objects.create(user=request.user, action='LEFT_POST', post=post)
                messages.success(request, "You have left the group.")
            else:
                messages.info(request, "You are not a member of this post.")

        # Handle clearing the activity log (only for the post owner)
        if 'clear_activity' in request.POST:
            if request.user == post.author:
                # Clear all activities related to the post
                Activity.objects.filter(post=post).delete()
                messages.success(request, "All recent activity has been cleared.")
            else:
                messages.error(request, "You do not have permission to clear the activity log.")

            return redirect('post_detail', pk=pk)

                
        return redirect('post_detail', pk=pk)

    # Get the members list, including the owner and the other members
    members = post.members.all()
    
    # Fetch the recent activities related to the post
    recent_activities = Activity.objects.filter(post=post).order_by('-timestamp')

    # Render the post detail page with the post, comments, and members
    return render(request, 'base/post_detail.html', {
        'post': post,
        'comments': comments,
        'members': members,  # Pass the members list to the template
        'recent_activities': recent_activities,  # Pass recent activities
    })

# View to edit an existing post
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Only allow the post owner to edit the post
    if post.author != request.user:
        messages.error(request, "You do not have permission to edit this post.")
        return redirect('post_detail', pk=pk)

    # If the request is POST, handle form submission
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        topics = request.POST.getlist('topics')  # Get the selected topics (multiple)

        # Ensure the title and content are not empty
        if title and content:
            # Update the post
            post.title = title
            post.content = content

            # Update the topics (ManyToMany field)
            post.topics.clear()  # Remove any existing topics
            for topic_name in topics:
                topic_obj, created = Topic.objects.get_or_create(name=topic_name)  # Get or create topic
                post.topics.add(topic_obj)  # Add the topic to the post

            post.save()

            # Log the edit as an activity
            Activity.objects.create(user=request.user, action='EDITED_POST', post=post)

            messages.success(request, "Post updated successfully.")
            return redirect('home')

    # If the request is GET, pre-fill the form with existing data
    return render(request, 'base/edit_post.html', {
        'post': post,
        'topics': post.topics.all(),  # Send current topics to the template
        'all_topics': Topic.objects.all(),  # Send all available topics to the template for selection
    })

# View to delete a post
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Only allow the post owner to delete the post
    if post.author != request.user:
        messages.error(request, "You do not have permission to delete this post.")
        return redirect('post_detail', pk=pk)

    post.delete()

    # Log the deletion as an activity
    #Activity.objects.create(user=request.user, action='DELETED_POST', post=post)

    messages.success(request, "Post deleted successfully.")
    return redirect('home')

# View to delete a comment on a post
def delete_comment(request, pk, comment_id):
    post = get_object_or_404(Post, pk=pk)
    comment = get_object_or_404(Comment, pk=comment_id)

    # Only allow the post owner or comment owner to delete the comment
    if request.user == post.author or request.user == comment.author:
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this comment.")
    
    return redirect('post_detail', pk=pk)

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
