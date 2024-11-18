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
from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home_view, name='home'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('search/', views.search, name='search'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings, name='settings'),  # Unified settings page
    path('login/', LoginView.as_view(template_name='base/login.html'), name='login'),
    path('admin/', admin.site.urls, name='admin'),
    path('register/', views.register, name='register'),
    path('profile/<int:pk>/', views.user_profile_view, name='user_profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('settings/', views.settings_view, name='settings'),
    path('delete_account/', views.delete_account, name='delete_account'),
    
    # Password change on the settings page
    path('settings/change_password/', PasswordChangeView.as_view(
        template_name='base/change_password.html',
        success_url=reverse_lazy('password_change_done')
    ), name='change_password'),
    path('settings/change_password_done/', PasswordChangeDoneView.as_view(
        template_name='base/change_password_done.html'
    ), name='password_change_done'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

