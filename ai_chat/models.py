from django.db import models
from django.utils import timezone

class ChatHistory(models.Model):
    session_id = models.CharField(max_length=100)
    user_message = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Chat {self.session_id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"