from django.contrib import admin
from .models import ChatHistory, ChatConversion, ChatLead

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user_message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('session_id', 'user_message', 'bot_response')
    readonly_fields = ('session_id', 'user_message', 'bot_response', 'created_at')

@admin.register(ChatConversion)
class ChatConversionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'conversion_type', 'converted_at', 'completed')
    list_filter = ('conversion_type', 'converted_at', 'completed')
    search_fields = ('session_id', 'user_message')
    readonly_fields = ('session_id', 'user_message', 'conversion_type', 'converted_at')

@admin.register(ChatLead)
class ChatLeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company', 'source', 'created_at', 'converted')
    list_filter = ('source', 'created_at', 'converted')
    search_fields = ('name', 'email', 'company', 'message')
    list_editable = ('converted',)