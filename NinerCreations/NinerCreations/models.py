from django.db import models
from django.contrib.auth.models import User
import os
from django.conf import settings
from django.core.files.storage import default_storage

class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    topics = models.ManyToManyField(Topic, related_name="posts", blank=True)

    def __str__(self):
        return self.title

    @property
    def activity_type(self):
        return "Post"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        author_name = self.author.username if self.author else "Guest"
        return f"Comment by {author_name} on {self.post}"

    @property
    def activity_type(self):
        return "Comment"


class Activity(models.Model):
    ACTION_CHOICES = [
        ('CREATED_ROOM', 'Created a Room'),
        ('CREATED_POST', 'Created a Post'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} on {self.timestamp}"


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    github_link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# The Profile model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, default='')
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        default='profile_pictures/profile-placeholder.png'
    )

    def __str__(self):
        return self.user.username

    def get_profile_picture_url(self):
        """
        Returns the profile picture URL if it exists, or the static placeholder otherwise.
        """
        if self.profile_picture and default_storage.exists(self.profile_picture.name):
            return self.profile_picture.url
        return os.path.join(settings.STATIC_URL, 'images/profile-placeholder.png')