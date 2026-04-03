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

class ChatConversion(models.Model):
    session_id = models.CharField(max_length=100)
    user_message = models.TextField()
    conversion_type = models.CharField(max_length=50)  # 'demo_request', 'contact_request', etc.
    converted_at = models.DateTimeField(default=timezone.now)
    completed = models.BooleanField(default=False)  # Se o usuário completou a ação

    class Meta:
        ordering = ['-converted_at']

    def __str__(self):
        return f"Conversion {self.conversion_type} - {self.session_id}"

class ChatLead(models.Model):
    session_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=100, blank=True)
    message = models.TextField(blank=True)
    source = models.CharField(max_length=50, default='chatbot')  # 'chatbot', 'form', etc.
    created_at = models.DateTimeField(default=timezone.now)
    converted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Lead {self.name or 'Anônimo'} - {self.created_at.strftime('%Y-%m-%d')}"