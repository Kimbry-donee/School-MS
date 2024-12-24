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
            
            # Attempt to authenticate without logging in
            user = authenticate(request, username=username, password=password)
            if user and not user.is_active:
                # Add a custom message if the user is inactive
                messages.error(request, "This account is inactive. Please contact support.")
                return redirect("/admin/login/")  # Redirect back to the login page

        # Continue processing the request if no issues
        response = self.get_response(request)
        return response
        
