from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def superuser_required(view_func):
    """
    Decorator: Restricts access to a view to only superusers.
    - Redirects to login page if user is not authenticated.
    - Redirects to home page with error message if user is not a superuser.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            # If the user is not logged in, send them to the login page
            return redirect("login")

        if not request.user.is_superuser:
            # If the user is logged in but not a superuser, show error and redirect home
            messages.error(request, "Only superusers can simulate chats.")
            return redirect("home")

        # If authenticated and a superuser, allow access to the view
        return view_func(request, *args, **kwargs)

    return wrapper