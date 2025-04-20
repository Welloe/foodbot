"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from chatbot.views import home, simulate_chats_page, simulate_chats_stream, vegetarian_responses_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home, name='home'),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="login.html",
            redirect_authenticated_user=True,
            next_page="/"  # 👈 This ensures redirection to home
        ),
        name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path('simulate-chats/', simulate_chats_page, name='simulate_chats'),
    path('simulate-chats-stream/', simulate_chats_stream, name='simulate_chats_stream'),
    path("admin/", admin.site.urls),
    path("vegetarians/", vegetarian_responses_view, name="vegetarians"),
    path("api/", include("chatbot.urls")),
]
