from django.contrib import messages
from django.shortcuts import redirect
from functools import wraps

def superuser_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")  # ensure they're logged in first
        if not request.user.is_superuser:
            messages.error(request, "Only superusers can simulate chats.")
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return wrapper