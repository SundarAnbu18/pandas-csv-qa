"""Registering a model here gives you a free web UI at /admin/ to browse it.

To use it once: python manage.py createsuperuser
"""

from django.contrib import admin

from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['question', 'created_at']
    search_fields = ['question', 'answer']
