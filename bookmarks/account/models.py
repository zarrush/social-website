from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True, null=True)

    def __str__(self):
        return f'Profile of {self.user.username}'


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='posts', 
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    body = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return f'{self.title} by {self.author.username}'
    
    @property
    def total_likes(self):
        return self.likes.count()
    
    @property
    def total_comments(self):
        return self.comments.count()


class Comment(models.Model):
    post = models.ForeignKey(
        Post, 
        related_name='comments', 
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='comments', 
        on_delete=models.CASCADE
    )
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.title}'


class Like(models.Model):
    post = models.ForeignKey(
        Post, 
        related_name='likes', 
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='likes', 
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('post', 'user')
        ordering = ['-created']
    
    def __str__(self):
        return f'{self.user.username} liked {self.post.title}'


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='following', 
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='followers', 
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created']
    
    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'
    
    def clean(self):
        if self.follower == self.following:
            raise ValidationError("Users cannot follow themselves.")