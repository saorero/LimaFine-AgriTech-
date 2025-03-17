from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class UserProfile(models.Model): # Model for Django authentication system
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    county = models.CharField(max_length=100)
    phoneNo = models.CharField(max_length=15)
    ROLE_CHOICES = (
        ('farmer', 'Farmer'),
        ('researcher', 'Researcher'),
        ('trader', 'Trader'),
        ('other', 'Other'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='farmer')

    # Followers logic, symmetric false to track who follows who, follow is not mutual Monday
    # Followers field added
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

# Store users post and timestamp
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    file = models.FileField(upload_to='uploads/', blank=True, null=True)  # Allows image/pdf uploads 11/03/2025
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

   
    # Function to keep count of the number of likes related to a post and returns it
    def totalLikes(self):
        return self.likes.count()
    
    
    def __str__(self):
        return f"{self.user.username} - {self.content[:20]}"


# Model that keep track of likes 13
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = ('user', 'post')# Ensures that a user can only like a post once

    def __str__(self):
        return f"{self.user.username} liked {self.post.user.username}'s post"


# Model to keep track of comments made on a post
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.id}"

