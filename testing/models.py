from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse

# --- MODELLER ---

profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True, default='profiles/default.jpg')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.user.username)
        super().save(*args, **kwargs)

    def _str_(self):
        return f"{self.user.username}'s Profile"

    @property
    def followers_count(self):
        return self.user.followers.count()

    @property
    def following_count(self):
        return self.user.following.count()

    @property
    def post_count(self):
        return self.user.posts.count()

    @property
    def total_likes(self):
        return sum(post.likes.filter(is_like=True).count() for post in self.user.posts.all())


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def _str_(self):
        return self.name


class Post(models.Model):
    def like_count(self):
        return self.likes.filter(is_like=True).count()
    CATEGORY_CHOICES = [
        ('book', 'Book'),
        ('article', 'Article'),
        ('recipe', 'Food&Recipe'),
        ('movie', 'Movies'),
        ('activity', 'Sport Activities'),
        ('other', 'Others'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200, verbose_name="Title")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField(verbose_name="Content")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Category")
    image = models.ImageField(upload_to='posts/', blank=True, null=True, verbose_name="Image")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0, verbose_name="Number of Views")
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def _str_(self):
        return f"{self.title} - {self.author.username}"

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})

    @property
    def dislike_count(self):
        return self.likes.filter(is_like=False).count()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(verbose_name="Comment")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def _str_(self):
        return f"{self.user.username} - {self.post.title}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    is_like = models.BooleanField(default=True, verbose_name="Like")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        verbose_name = "Like"
        verbose_name_plural = "Likes"

    def _str_(self):
        return f"{self.user.username} - {'Like' if self.is_like else 'Dislike'} - {self.post.title}"


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = "Follower"
        verbose_name_plural = "Followers"

    def _str_(self):
        return f"{self.follower.username} → {self.following.username}"


class Report(models.Model):
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('abuse', 'Abusive Content'),
        ('other', 'Other'),
    ]
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.reporter.username} reported {self.post.title} ({self.reason})"


class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def _str_(self):
        return f"{self.user.username} saved {self.post.title}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.user.username} - {self.message}"