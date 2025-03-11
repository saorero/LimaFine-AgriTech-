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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.content[:20]}"