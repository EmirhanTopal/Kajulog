from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, Post, Comment, Like, Follow


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profiller'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'view_count', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'view_count')
    list_editable = ('category',)
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('author', 'title', 'slug', 'content', 'category')
        }),
        ('Medya', {
            'fields': ('image',)
        }),
        ('İstatistikler', {
            'fields': ('view_count', 'created_at', 'updated_at')
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('content', 'user_username', 'post_title')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'is_like', 'created_at')
    list_filter = ('is_like',)
    search_fields = ('user_username', 'post_title')
    readonly_fields = ('created_at',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    search_fields = ('follower_username', 'following_username')
    readonly_fields = ('created_at',)



admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)