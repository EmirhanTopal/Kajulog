from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('post/<slug:slug>/like/', views.toggle_like, name='toggle_like'),
    
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', views.signup, name='signup'),

    path('create/', views.create_post, name='create_post'),

    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/', views.my_profile, name='my_profile'),
    path('profile/<str:username>/toggle-follow/', views.toggle_follow, name='toggle_follow'),
    path('profile/<slug:slug>/', views.profile_detail, name='profile_detail'),
    
    path('update-comment/', views.update_comment, name='update_comment'),
    path('toggle-like/<slug:slug>/', views.toggle_like, name='toggle_like'),
    path('delete-comment/', views.delete_comment, name='delete_comment'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)