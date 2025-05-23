from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Post, Comment, Like
from .forms import CommentForm
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms import PostForm

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # kullanıcıyı oluştur ama login olmasın
            return redirect('login')  # login sayfasına yönlendir
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def post_list(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    
    posts = Post.objects.all()

    if query:
        posts = posts.filter(title__icontains=query)
    
    if category:
        posts = posts.filter(category=category)

    return render(request, 'post_list.html', {'posts': posts, 'query': query, 'category': category})

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.view_count += 1
    post.save()
    comments = post.comments.all()
    form = CommentForm()

    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })

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
    return redirect('post_detail', slug=slug)

@login_required
def toggle_like(request, slug):
    post = get_object_or_404(Post, slug=slug)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.is_like = not like.is_like
        like.save()
    return redirect('post_detail', slug=slug)

