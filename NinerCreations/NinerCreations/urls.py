"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from .views import profile_view
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from django.conf.urls import handler400
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home_view, name='home'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),  # New URL pattern for post detail and comments
    path('create-post/', views.create_post, name='create_post'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),  # New URL pattern for post detail and comments
    path('post/<int:pk>/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('search/', views.search, name='search'),  # Added search URL
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('login/', LoginView.as_view(template_name='base/login.html'), name='login'),    path('admin/', admin.site.urls, name='admin'),
    path('register/', views.register, name='register'),
    path('profile/<int:pk>/', views.user_profile_view, name='user_profile'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Add this line
    path('add_project/', views.add_project, name='add_project'),
    path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('edit-project/<int:project_id>/', views.edit_project, name='edit_project'),
    path('settings/', views.settings, name='settings'),
    path('profile/', views.profile, name='profile'),
    path('delete-account/', views.delete_account, name='delete_account'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = 'NinerCreations.views.handle_invalid_topic_id'