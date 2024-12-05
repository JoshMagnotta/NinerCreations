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
from .models import Profile
from .forms import ProfileForm
from .models import Post, Comment, Project, Profile
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Topic, Activity

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


def home_view(request):
    topic_id = request.GET.get('topic')

    # Validate topic_id to ensure it's an integer
    if topic_id:
        try:
            topic_id = int(topic_id)
        except ValueError:
            # Pass the error_message context to the 400.html template
            return render(request, '400.html', {'error_message': 'Invalid topic parameter.'}, status=400)

    # Filter posts by topic if provided, otherwise return all posts
    if topic_id:
        posts = Post.objects.filter(topics__id=topic_id).order_by('-created_at')
        recent_posts = Post.objects.filter(topics__id=topic_id).order_by('-created_at')[:10]
    else:
        posts = Post.objects.all().order_by('-created_at')
        recent_posts = Post.objects.all().order_by('-created_at')[:10]

    # Retrieve comments related to the filtered posts
    post_ids = posts.values_list('id', flat=True)
    recent_comments = Comment.objects.filter(post__id__in=post_ids).order_by('-created_at')[:10]

    # Combine posts and comments, sorted by creation date, to get the 10 most recent activities
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
        'topics': topics,
    })

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    recent_rooms = Post.objects.filter(author=request.user).order_by('-created_at')[:5]
    recent_posts = Post.objects.filter(author=request.user).order_by('-created_at')[:10]
    recent_comments = Comment.objects.filter(author=request.user).order_by('-created_at')[:10]
    projects = Project.objects.filter(user=request.user)

    recent_activities = sorted(
        list(recent_posts) + list(recent_comments),
        key=lambda x: x.created_at,
        reverse=True
    )[:10]

    return render(request, 'base/profile.html', {
        'profile': profile,
        'recent_rooms': recent_rooms,
        'recent_activities': recent_activities,
        'projects': projects,
    })



def user_profile_view(request, pk):
    # Fetch the user object for the profile being viewed
    profile_user = get_object_or_404(User, pk=pk)
    profile, created = Profile.objects.get_or_create(user=profile_user)

    # Fetch recent rooms, posts, and comments by the profile owner
    recent_rooms = Post.objects.filter(author=profile_user).order_by('-created_at')[:5]
    recent_posts = Post.objects.filter(author=profile_user).order_by('-created_at')[:10]
    recent_comments = Comment.objects.filter(author=profile_user).order_by('-created_at')[:10]

    # Combine posts and comments, sorted by creation date
    recent_activities = sorted(
        list(recent_posts) + list(recent_comments),
        key=lambda x: x.created_at,
        reverse=True
    )[:10]

    # Fetch the completed projects for this profile owner
    projects = Project.objects.filter(user=profile_user).order_by('-created_at')

    # Include bio and profile picture in the context
    context = {
        'profile_user': profile_user,  # User whose profile is being viewed
        'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
        'bio': profile.bio or "This user has not added a bio yet.",
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
        privacy = request.POST.get('privacy', 'public')

        # Ensure the user is logged in
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to create a post.")
            return redirect('login')

        if title and content:
            # Create the post
            post = Post.objects.create(
                author=request.user,
                title=title,
                content=content,
                privacy=privacy
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
            # Fetch comments again to include the new one
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
            if post.privacy == "public":
                # Allow joining only for public posts
                if request.user not in post.members.all():
                    post.members.add(request.user)
                    Activity.objects.filter(post=post, user=request.user, action='JOINED_POST').delete()
                    Activity.objects.create(user=request.user, action='JOINED_POST', post=post)
                    messages.success(request, "You have joined the group.")
                else:
                    messages.info(request, "You are already a member of this post.")
            else:
                messages.error(request, "You cannot join a private group unless invited.")

        elif 'leave' in request.POST:
            # Allow leaving for both public and private posts
            if request.user in post.members.all():
                post.members.remove(request.user)
                Activity.objects.filter(post=post, user=request.user, action='LEFT_POST').delete()
                Activity.objects.create(user=request.user, action='LEFT_POST', post=post)
                messages.success(request, "You have left the group.")
            else:
                messages.info(request, "You are not a member of this post.")

        # Handle clearing the activity log (only for the post owner)
        if 'clear_activity' in request.POST:
            if request.user == post.author:
                Activity.objects.filter(post=post).delete()
                messages.success(request, "All recent activity has been cleared.")
            else:
                messages.error(request, "You do not have permission to clear the activity log.")
            
            return redirect('post_detail', pk=pk)

        return redirect('post_detail', pk=pk)

    # Get the members list, including the owner and the other members
    members = post.members.all()

    # Fetch recent activities related only to joining or leaving the post
    recent_activities = Activity.objects.filter(
        post=post,
        action__in=['JOINED_POST', 'LEFT_POST']
    ).order_by('-timestamp')

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
        privacy = request.POST.get('privacy', post.privacy)

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


def settings(request):
    return render(request, 'base/settings.html')

def login(request):
    return render(request, 'base/login.html')

#Register account stuff
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)  # Include `request.FILES` for file upload
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Please log in.')
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
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

# User Settings View
@login_required
def settings(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update ProfileForm for bio and profile picture
        form = ProfileForm(request.POST, request.FILES, instance=profile)

        # Get new values for first name, last name, username, and email
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Get and validate password inputs
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if form.is_valid():
            # Update user details
            user = request.user
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email

            # Handle password update if provided
            if password and password == confirm_password:
                user.set_password(password)

            # Save user and profile changes
            user.save()
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('settings')
        else:
            messages.error(request, "There was an error updating your profile.")

    else:
        form = ProfileForm(instance=profile)

    return render(request, 'base/settings.html', {
        'form': form,
        'profile': profile,
    })


# Delete Account View
@login_required
def delete_account(request):
    """
    View to handle account deletion for the logged-in user.
    """
    if request.method == "POST":
        user = request.user
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect('home')

    return render(request, 'base/delete_account.html')

