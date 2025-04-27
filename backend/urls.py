from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from chatbot.views import (
    home,
    simulate_chats_page,
    simulate_chats_stream,
    vegetarian_responses_view
)

"""
URL Configuration for the Backend Project.

Routes user requests to appropriate views.
For more information: https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

urlpatterns = [
    # Homepage
    path('', home, name='home'),

    # Authentication
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="login.html",
            redirect_authenticated_user=True,
            next_page="/"  # Redirect authenticated users to home
        ),
        name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Simulation pages (superuser only)
    path('simulate-chats/', simulate_chats_page, name='simulate_chats'),
    path('simulate-chats-stream/', simulate_chats_stream, name='simulate_chats_stream'),

    # Admin site
    path("admin/", admin.site.urls),

    # Vegetarian responses page
    path("vegetarians/", vegetarian_responses_view, name="vegetarians"),
]