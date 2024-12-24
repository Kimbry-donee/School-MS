# middleware.py
from django.utils.deprecation import MiddlewareMixin
from polls.models import School


class SchoolMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                request.current_school = request.user.profile.school
            except StaffProfile.DoesNotExist:
                # Optionally redirect to a page where user can set their school
                request.current_school = None