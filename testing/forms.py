from django import forms
from .models import Comment, Post, Profile
from .models import Tag

class PostForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'tag-select',
            'size': 6  # İsteğe göre yüksekliğini ayarlayabilirsin
        })
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'image', 'tags']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture']