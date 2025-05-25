from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .views import signup

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('post/<slug:slug>/like/', views.toggle_like, name='toggle_like'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),  # ← BURAYA DİKKAT
    path('signup/', signup, name='signup'),
    path('create/', views.create_post, name='create_post'),
]

