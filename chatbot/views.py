import os
import time
import random

from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response

from openai import OpenAI
from openai import APIConnectionError, RateLimitError, OpenAIError

from .models import ChatResponse
from .serializers import ChatResponseSerializer
from chatbot.utils import simulate_gpt_chats, self_learn_from_non_veg_responses
from chatbot.decorators import superuser_required

# Initialize OpenAI client
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
client = OpenAI()


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def vegetarian_responses(request):
    """
    API endpoint: Returns vegetarian/vegan chat responses for authenticated users.
    """
    queryset = ChatResponse.objects.filter(role='B', is_vegetarian_or_vegan=True)
    serializer = ChatResponseSerializer(queryset, many=True)
    return Response(serializer.data)


def home(request):
    """
    View: Render the homepage.
    """
    return render(request, "home.html")


@superuser_required
def simulate_chats_page(request):
    """
    View: Render the simulation control page for superusers.
    """
    return render(request, 'simulate_chats.html')


@superuser_required
def simulate_chats_stream(request):
    """
    Stream: Simulate chat responses in real-time and self-learn new non-vegetarian keywords.
    """
    def event_stream():
        # Clear old chat responses
        ChatResponse.objects.all().delete()
        yield "data: 🌀 Starting simulation...<br>\n\n"

        # Simulate 100 chat responses
        for i, msg in enumerate(simulate_gpt_chats(100, stream=True), 1):
            safe_msg = msg.replace("\n", "<br>")
            yield f"data: {i:03d}/100 → {safe_msg}<br>\n\n"
            time.sleep(0.05)  # Small delay for a smooth stream

        # After simulation, learn new non-veg keywords
        yield "data: 🧐 Analyzing non-veggie responses...<br>\n\n"
        keywords = self_learn_from_non_veg_responses()

        if keywords:
            for word in keywords:
                yield f"data: ➕ Learned new keyword: <b>{word}</b><br>\n\n"
        else:
            yield "data: ✅ No new keywords learned.<br>\n\n"

        yield "data: ✅ Done! Returning to homepage...<br>\n\n"

    # Return the event stream as a server-sent event
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


@login_required
def vegetarian_responses_view(request):
    """
    View: Display vegetarian/vegan chat responses to logged-in users.
    """
    responses = ChatResponse.objects.filter(is_vegetarian_or_vegan=True).order_by("-created_at")
    return render(request, "vegetarians.html", {"responses": responses})
