from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import User  # adjust the import based on your project structure

def session_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_login_id')
        if not user_id:
            messages.error(request, "Please login to continue.")
            return redirect('user_login')
        # Optionally, check if the user exists and attach it to the request
        try:
            request.user_instance = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            messages.error(request, "User not found. Please login again.")
            return redirect('user_login')
        return view_func(request, *args, **kwargs)
    return wrapper
