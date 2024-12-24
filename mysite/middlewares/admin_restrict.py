# middleware/custom_middleware.py

from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponseForbidden


class AdminAccessControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define the admin paths to exclude from the redirection logic
        excluded_paths = ['/admin/login/', '/admin/logout/', '/admin/password_reset/', '/admin/reset/']

        # Check if the request path starts with '/admin/' but not in excluded paths
        if request.path.startswith('/admin/') and request.path not in excluded_paths:
            # Check if the user is not authenticated
            if not request.user.is_authenticated:
                # Redirect the non-authenticated user to the login page
                return redirect(settings.LOGIN_URL)

            # Check if the user is authenticated but not a staff member
            if not request.user.is_staff:
                # Return a 403 Forbidden response
                return HttpResponseForbidden("You do not have permission to access the admin area.")

        # Proceed with the response
        response = self.get_response(request)
        return response