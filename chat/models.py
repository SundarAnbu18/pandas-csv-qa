"""A model = one table in the database.

Every attribute below becomes a column. Django writes the SQL for you.
After changing this file, run:
    python manage.py makemigrations
    python manage.py migrate
"""

from django.db import models


class Message(models.Model):
    """One round of the conversation: what you asked, what the AI replied."""

    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # filled in automatically

    class Meta:
        ordering = ['created_at']  # oldest first, like a real chat window

    def __str__(self):
        """What this row looks like in the Django admin / shell."""
        return self.question[:50]
