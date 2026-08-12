"""The main address book of the whole site.

Django looks here first for every incoming request. `include()` hands the URL
over to an app's own urls.py, which keeps this file short.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chat.urls')),  # "/" and everything under it -> chat app
]
