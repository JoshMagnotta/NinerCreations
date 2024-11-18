from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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
        return f"Comment by {self.author} on {self.post}"

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

class Profile(models.Model):
    # One-to-one relationship with the User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)  # Bio field for user profile

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Automatically create or update the Profile whenever a User is created/updated
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default.png')

    def __str__(self):
        return self.user.username