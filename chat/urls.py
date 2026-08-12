"""URLs for the chat app: which address runs which view.

The `name=` is a nickname. In templates you write {% url 'chat' %} instead of
hard-coding "/", so if the address changes later, nothing breaks.
"""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.chat, name='chat'),
    path('clear/', views.clear, name='clear'),
]
