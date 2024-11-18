from django.contrib import admin
from .models import Post, Comment, Topic
from .models import Profile 

# admin.site.register(NinerCreations)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Topic)
admin.site.register(Profile)
