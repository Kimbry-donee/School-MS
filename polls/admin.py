from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import *
from django.db.models import Q
from django.contrib.auth.models import Permission

        
class StaffProfileInline(admin.TabularInline):
  model = StaffProfile
  extra = 1
class CustomUserAdmin(UserAdmin):
    inlines = [StaffProfileInline]
    def get_inline_instances(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return super().get_inline_instances(request, obj)
        
    def get_queryset(self, request):
      qs = super().get_queryset(request)
      #If the user is a limited superuser
      if getattr(request.user, 'is_limited_superuser', False):
        # Exclude superuser accounts for limited superusers
        qs = qs.exclude(is_superuser=True)
        # Ensure they only see accounts that are active or not deactivated by a full superuser
        qs = qs.filter(
            (Q(is_active=True) | Q(is_active=False, deactivated_by_superuser=False)) &
            (Q(staffprofile__school__is_account_active=True) | Q(staffprofile__school__isnull=True))  # Show users without a school
        )
        # If the user is not a superuser, exclude superusers from the view
      elif not request.user.is_superuser:
        qs = qs.exclude(is_superuser=True)
      return qs
    
    def save_model(self, request, obj, form, change):
        # Allow editing superuser accounts only if logged-in user is a superuser
        if change and obj.is_superuser and not request.user.is_superuser:
            return  # Prevent changes to superusers if user isn't a superuser

            # Ensure only superusers can create new superusers
        if not change and request.user.is_superuser:
            obj.is_superuser = True
            obj.is_staff = True
            obj.deactivated_by_superuser = True# Set as staff by default
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        # Allow change permission only if the object being edited is a superuser
        if obj and request.user.is_superuser:
            return obj.is_superuser
    # Limited superuser can edit all users
        if obj and getattr(request.user, 'is_limited_superuser', False):
            return True
    # For all other cases, fall back to the default permission check
        return super().has_change_permission(request, obj)
        
    def has_delete_permission(self, request, obj=None):
      # superuser can only delete other superuser
        if obj and request.user.is_superuser:
          return obj.is_superuser
        return super().has_delete_permission(request, obj)
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        # Hide 'is_limited_superuser' when editing a superuser account
        if obj and request.user.is_superuser and obj.is_superuser:
            fieldsets[1][1]['fields'] = [field for field in fieldsets[1][1]['fields'] if field != 'is_limited_superuser']
        return fieldsets
    
    def get_list_filter(self, request):
        # For regular users, restrict the filter fields to specific ones
        if request.user.is_superuser:
            return ['is_staff', 'is_active', 'is_limited_superuser', 'is_superuser','deactivated_by_superuser' ]
        return ['is_staff', 'is_active', 'is_limited_superuser']

    
    def get_list_display(self, request):
        # If the user is a superuser, include 'is_superuser' in list_display, otherwise exclude it
        list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_limited_superuser')
        if request.user.is_superuser:
            list_display += ('is_superuser','deactivated_by_superuser')
        return list_display
    # Register CustomUser with the custom admin settings
    fieldsets = [
      ('PERSONAL INFO', {'fields': ['username','email', 'first_name', 'last_name']}),
      ('PERMISSION', {'fields': ['is_staff', 'is_active', 'is_limited_superuser', ]}),
      ('GROUP AUTHORISED', {'fields': ['user_permissions', 'groups']})
      ]
    # Define the display fields for the user model in the admin
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_limited_superuser', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    ordering = ('username',)
admin.site.register(CustomUser, CustomUserAdmin)

class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'school')
    search_fields = ('school__name', 'user__first_name', 'user__last_name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # If the user is a limited superuser
        if getattr(request.user, 'is_limited_superuser', False):
            # Show their own profile and profiles of regular users only
            return qs.filter(Q(user=request.user) | Q(user__is_superuser=False))
        
        # If the user is a regular user, restrict them to only seeing their own profile
        elif not request.user.is_superuser:
            return qs.filter(user=request.user)
        # Superusers see all profiles, including other superuser profiles
        return qs
        #restrict superuser from edit profile
    def has_change_permission(self, request, obj=None):
        return not request.user.is_superuser
    def has_add_permission(self, request):
        return not request.user.is_superuser
admin.site.register(StaffProfile, StaffProfileAdmin)

class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'school')
    def get_model_perms(self, request):
        if request.user.is_superuser:
            return {}
        return super().get_model_perms(request)
    
    #Show school field for only Superusers
    def get_fields(self, request, obj=None):
      if request.user.is_limited_superuser:
        return ('name', 'age', 'school')
      return ('name', 'age')  # Hide 'school' from the form for none Superusers

    def save_model(self, request, obj, form, change):
        # Automatically set the school to the headmaster's school for new students
        if not request.user.is_limited_superuser:
          obj.school = request.user.profile.school  # Set the school unconditionally
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        # Restrict the queryset to students from the headmaster's school
        qs = super().get_queryset(request)
        if request.user.is_limited_superuser:
            return qs  # M.D see all students
        return qs.filter(school=request.user.profile.school)

admin.site.register(Student, StudentAdmin)

""" === HERE BELOW FOR SCHOOL === """

def deactivate_school_accounts(modeladmin, request, queryset):
  """Action to deactivate all user accounts linked to selected schools."""
  for school in queryset:
    CustomUser.objects.filter(staffprofile__school=school).update(is_active=False)  # Adjust 'profile__school' as per your models
    school.is_account_active = False
    school.save()
deactivate_school_accounts.short_description = "Deactivate all accounts for selected schools"

def activate_school_accounts(modeladmin, request, queryset):
  """Activate all user accounts linked to selected schools."""
  for school in queryset:
    CustomUser.objects.filter(staffprofile__school=school).update(is_active=True)  # Adjust profile__school as needed
    school.is_account_active =True
    school.save()
activate_school_accounts.short_description = "Activate all accounts for selected schools"

class StatusFilter(admin.SimpleListFilter):
    title = 'Status'  # Set the filter title
    parameter_name = 'is_account_active'  # The model field to filter on

    def lookups(self, request, model_admin):
        """Define filter options."""
        return [
            ('1', 'Active'),   # Show 'Active' instead of 'Yes'
            ('0', 'Inactive'), # Show 'Inactive' instead of 'No'
        ]

    def queryset(self, request, queryset):
        """Return the filtered queryset based on selected option."""
        if self.value() == '1':
            return queryset.filter(is_account_active=True)
        elif self.value() == '0':
            return queryset.filter(is_account_active=False)
        return queryset

class SchoolAdmin(admin.ModelAdmin):
    actions = [deactivate_school_accounts, activate_school_accounts]
    list_display = ('name', 'colored_status', 'is_account_active')
    search_fields = ['name']
    list_filter = [StatusFilter]
      
    def colored_status(self, obj):
      """display status with color green=#77fc03 red=#fc3503"""
      
      color='#fc3503' if not obj.is_account_active else '#77fc03'
      return format_html(
        '<span style="color : {}; font-weight: bold">{}</span>', 
        color, 
        'Inactive' if not obj.is_account_active else 'Active'
        )
    colored_status.short_description = 'Account Status'
    
    def get_actions(self, request):
        """Only show the deactivate action for superusers."""
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'deactivate_school_accounts' in actions:
                del actions['deactivate_school_accounts']
            if 'activate_school_accounts' in actions:
                del actions['activate_school_accounts']
        return actions
    
    def has_change_permission(self, request, obj=None):
        return not request.user.is_superuser
    def has_add_permission(self, request):
        return not request.user.is_superuser
admin.site.register(School, SchoolAdmin)
