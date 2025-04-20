from django.urls import path
from .views import chat, vegetarian_responses

urlpatterns = [
    path("chat/", chat),
]