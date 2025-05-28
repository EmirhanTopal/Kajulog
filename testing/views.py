from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib import messages

from .models import Profile, Post, Comment, Like, Follow
from .forms import PostForm, CommentForm, ProfileUpdateForm
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.db.models import Q

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from django.utils import timezone
from datetime import timedelta
from .models import Activity
from django.db.models import Count

from .models import Activity, Like, Follow, Tag


def posts_by_tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    posts = tag.posts.all()
    return render(request, 'posts_by_tag.html', {'tag': tag, 'posts': posts})


@login_required
def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post başarıyla güncellendi.")
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(request, 'edit_post.html', {'form': form, 'post': post})


@login_required
@require_POST
def toggle_like(request, slug):
    post = get_object_or_404(Post, slug=slug)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.is_like = not like.is_like
        like.save()
    else:
        like.is_like = True
        like.save()

    # Activity Kaydı Ekle
    if like.is_like:
        Activity.objects.create(user=request.user, action='like', post=post)

    return redirect('post_detail', slug=slug)

@login_required
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)
    if request.user == target_user:
        messages.warning(request, "Kendini takip edemezsin!")
        return redirect('profile_detail', slug=target_user.profile.slug)

    follow, created = Follow.objects.get_or_create(follower=request.user, following=target_user)
    if not created:
        follow.delete()
        messages.success(request, f"{target_user.username} takibi bırakıldı.")
    else:
        messages.success(request, f"{target_user.username} takip edildi.")
        # Activity Kaydı Ekle
        Activity.objects.create(user=request.user, action='follow', target_user=target_user)

    return redirect('profile_detail', slug=target_user.profile.slug)

@login_required
@require_POST
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.post = post
        comment.save()
        Activity.objects.create(user=request.user, action='comment', post=post)
        messages.success(request, "Yorumun eklendi.")
    return redirect('post_detail', slug=slug)


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()  # Burası önemli! Tagleri de kaydetmek için.
            messages.success(request, "Gönderin başarıyla oluşturuldu.")
            Activity.objects.create(user=request.user, action='post', post=post)
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

@login_required
def followers_list(request, slug):
    profile_user = get_object_or_404(User, profile__slug=slug)
    followers = profile_user.followers.all()

    context = {
        'profile_user': profile_user,
        'followers': followers,
    }
    return render(request, 'followers_list.html', context)

@login_required
def following_list(request, slug):
    profile_user = get_object_or_404(User, profile__slug=slug)
    following = profile_user.following.all()

    context = {
        'profile_user': profile_user,
        'following': following,
    }
    return render(request, 'following_list.html', context)

@login_required
@require_POST
def delete_comment(request):
    data = json.loads(request.body)
    comment_id = data.get('comment_id')

    try:
        comment = Comment.objects.get(id=comment_id, user=request.user)
        comment.delete()
        return JsonResponse({'success': True})
    except Comment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Yorum bulunamadı veya yetkiniz yok.'})


@login_required
def my_profile(request):
    profile = request.user.profile
    posts = request.user.posts.all()
    followers = request.user.followers.count()
    following = request.user.following.count()

    context = {
        'profile': profile,
        'posts': posts,
        'followers': followers,
        'following': following,
    }
    return render(request, 'my_profile.html', context)

@login_required
def profile_detail(request, slug):
    profile_user = get_object_or_404(User, profile__slug=slug)
    profile = profile_user.profile
    posts = profile_user.posts.all()
    is_following = False

    if request.user != profile_user:
        is_following = profile_user.followers.filter(follower=request.user).exists()

    context = {
        'profile_user': profile_user,
        'profile': profile,
        'posts': posts,
        'is_following': is_following,
    }
    return render(request, 'profil_page.html', context)

def home(request):
    activities = Activity.objects.order_by('-timestamp')[:10]
    one_week_ago = timezone.now() - timedelta(days=7)
    popular_posts = Post.objects.filter(likes__created_at__gte=one_week_ago).annotate(like_count=Count('likes')).order_by('-like_count')[:3]
    tags = Tag.objects.all()

    return render(request, 'home.html', {
        'activities': activities,
        'popular_posts': popular_posts,
        'tags': tags,
    })

@login_required
@require_POST
def update_comment(request):
    data = json.loads(request.body)
    comment_id = data.get('comment_id')
    content = data.get('content')

    try:
        comment = Comment.objects.get(id=comment_id, user=request.user)
        comment.content = content
        comment.save()
        return JsonResponse({'success': True, 'content': comment.content})
    except Comment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Comment not found or permission denied.'})

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profilin başarıyla güncellendi.")
            return redirect('profile_detail', slug=profile.slug)
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'edit_profile.html', {'form': form})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Gönderin başarıyla oluşturuldu.")
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

@login_required
def post_list(request):
    query = request.GET.get('q')
    filter_type = request.GET.get('type', 'all') 
    category = request.GET.get('category') 

    posts = Post.objects.all()
    users = User.objects.all()

    if category:
        posts = posts.filter(category=category)

    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(content__icontains=query))
        users = users.filter(username__icontains=query)

    # Filtre butonu seçimi
    if filter_type == 'users':
        posts = Post.objects.none()
    elif filter_type == 'posts':
        users = User.objects.none()

    search_made = bool(query)

    one_week_ago = timezone.now() - timedelta(days=7)
    popular_posts = Post.objects.filter(likes__created_at__gte=one_week_ago).annotate(like_count=Count('likes')).order_by('-like_count')[:3]
    activities = Activity.objects.order_by('-timestamp')[:10]
    tags = Tag.objects.all()

    context = {
        'posts': posts,
        'users': users,
        'query': query,
        'filter_type': filter_type,
        'search_made': search_made,
        'category': category,
        'activities': activities,
        'popular_posts': popular_posts,
        'tags': tags,
    }

    return render(request, 'post_list.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.view_count += 1
    post.save()

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        comment_id = data.get('comment_id')
        new_content = data.get('content')

        try:
            comment = Comment.objects.get(id=comment_id, user=request.user)
            comment.content = new_content
            comment.save()
            return JsonResponse({'success': True})
        except:
            return JsonResponse({'success': False})

    comments = post.comments.all()
    form = CommentForm()

    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Kayıt başarıyla oluşturuldu, giriş yapabilirsin.")
            return redirect('login')
        else:
            # Form geçerli değilse aynı sayfayı hata mesajları ile göster
            return render(request, 'signup.html', {'form': form})
    else:
        form = UserCreationForm()
        return render(request, 'signup.html', {'form': form})

