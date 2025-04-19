import os
import random
from openai import OpenAI
from openai import APIConnectionError, RateLimitError, OpenAIError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ChatResponse
from .serializers import ChatResponseSerializer
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@api_view(['POST'])
def chat(request):
    user_message = request.data.get("message")

    if not user_message:
        return Response({"error": "No message provided"}, status=400)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content
    except (APIConnectionError, RateLimitError, OpenAIError) as e:
        print(f"[OpenAI ERROR] {e} → Using fallback")
        fake_replies = [
            "I like pizza, hummus, and tofu!",
            "My top 3 are sushi, falafel, and pad thai!",
            "Pasta, stir-fried veggies, and lentil soup!"
        ]
        reply = random.choice(fake_replies)
    
    # After generating 'reply':
    ChatResponse.objects.create(
        role='B',
        message=reply,
        is_vegetarian=check_if_vegetarian(reply)  # This function we'll add next
    )

    return Response({"reply": reply})

def check_if_vegetarian(text):
    non_veg_keywords = [
        "chicken", "beef", "pork", "bacon", "steak", "fish", "shrimp", "lamb", "meat",
        "salmon", "turkey", "duck", "anchovy", "tuna", "prosciutto", "ribs",
        "sausage", "ham", "veal", "pepperoni", "mutton", "crab", "lobster", "octopus"
    ]
    text_lower = text.lower()
    return not any(word in text_lower for word in non_veg_keywords)

@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def vegetarian_responses(request):
    queryset = ChatResponse.objects.filter(role='B', is_vegetarian_or_vegan=True)
    serializer = ChatResponseSerializer(queryset, many=True)
    return Response(serializer.data)
