from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def _str_(self):
        return f"{self.user.username}'s Profile"


class Post(models.Model):
    CATEGORY_CHOICES = [
        ('book', 'Kitap'),
        ('article', 'Makale'),
        ('recipe', 'Yemek Tarifi'),
        ('movie', 'Film'),
        ('activity', 'Spor Aktivitesi'),
        ('other', 'Diğer'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200, verbose_name="Başlık")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField(verbose_name="İçerik")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Kategori")
    image = models.ImageField(upload_to='posts/', blank=True, null=True, verbose_name="Görsel")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0, verbose_name="Görüntülenme Sayısı")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Gönderi"
        verbose_name_plural = "Gönderiler"

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
    content = models.TextField(verbose_name="Yorum")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Yorum"
        verbose_name_plural = "Yorumlar"

    def _str_(self):
        return f"{self.user.username} - {self.post.title}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    is_like = models.BooleanField(default=True, verbose_name="Beğeni")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        verbose_name = "Beğeni"
        verbose_name_plural = "Beğeniler"

    def _str_(self):
        return f"{self.user.username} - {'Like' if self.is_like else 'Dislike'} - {self.post.title}"


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = "Takip"
        verbose_name_plural = "Takipçiler"

    def _str_(self):
        return f"{self.follower.username} → {self.following.username}"
