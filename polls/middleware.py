# yourapp/middleware.py
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import authenticate

class InactiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/admin/login/" and request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")

            # Authenticate without logging in
            user = authenticate(request, username=username, password=password)
            if user and not user.is_active:
                # Add the inactive user message
                messages.error(request, "This account is inactive. Please contact support.")
                return redirect("/admin/login/")

        # Proceed with the request as normal
        response = self.get_response(request)
        return response