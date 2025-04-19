from rest_framework import serializers
from .models import ChatResponse

class ChatResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatResponse
        fields = ['id', 'role', 'message', 'is_vegetarian_or_vegan', 'created_at']