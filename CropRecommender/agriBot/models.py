
# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.TextField()
    rag_response = models.TextField()
    general_response = models.TextField()
    timestamp = models.DateTimeField(default=datetime.now)
    conversation_id = models.CharField(max_length=36, blank=True)  # UUID for grouping messages in a session

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.query[:50]} - {self.timestamp}"