from django.urls import path
from .views import chat, vegetarian_responses

urlpatterns = [
    path("chat/", chat),
    path("vegetarians/", vegetarian_responses),
]