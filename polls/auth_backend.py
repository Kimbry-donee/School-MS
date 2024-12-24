# yourapp/auth_backends.py
from django.contrib import messages
from django.contrib.auth.backends import ModelBackend
from django.shortcuts import redirect

class InactiveUserAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Use the default authentication method
        user = super().authenticate(request, username=username, password=password)
        if user is not None and not user.is_active:
            # If user is inactive, add a custom message
            messages.error(request, "This account is inactive. Please contact support.")
            return None  # Return None to prevent login
        return user