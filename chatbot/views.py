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
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from chatbot.utils import simulate_gpt_chats
from django.contrib import messages
from django.http import StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from chatbot.decorators import superuser_required

import time

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
client = OpenAI()

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

def home(request):
    return render(request, "home.html")

@superuser_required
def simulate_chats_page(request):
    return render(request, 'simulate_chats.html')

@superuser_required
def simulate_chats_stream(request):
    def event_stream():
        ChatResponse.objects.all().delete()
        yield "data: 🌀 Starting simulation...<br>\n\n"
        for i, msg in enumerate(simulate_gpt_chats(100, stream=True), 1):
            safe_msg = msg.replace("\n", "<br>")
            yield f"data: {i:03d}/100 → {safe_msg}<br>\n\n"
            time.sleep(0.05)

        yield "data: 🧠 Analyzing non-veggie responses...<br>\n\n"
        from chatbot.utils import self_learn_from_non_veg_responses
        keywords = self_learn_from_non_veg_responses()
        if keywords:
            for word in keywords:
                yield f"data: ➕ Learned new keyword: <b>{word}</b><br>\n\n"
        else:
            yield "data: ✅ No new keywords learned.<br>\n\n"
        yield "data: ✅ Done! Returning to homepage...<br>\n\n"

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

@login_required
def vegetarian_responses_view(request):
    responses = ChatResponse.objects.filter(is_vegetarian_or_vegan=True).order_by("-created_at")
    return render(request, "vegetarians.html", {"responses": responses})