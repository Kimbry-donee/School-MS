from django.db import models
from django.contrib import admin
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser, Permission

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_limited_superuser = models.BooleanField(default=False, verbose_name='Head Staff')
    # Add a new field to track whether the user was deactivated by a superuser
    deactivated_by_superuser = models.BooleanField(default=False, verbose_name='Activatory')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email


# Signal to assign permissions based on is_limited_superuser status
@receiver(post_save, sender=CustomUser)
def assign_limited_superuser_permissions(sender, instance, **kwargs):
    if instance.is_limited_superuser and not instance.is_superuser:
        # Assign all permissions except specific ones reserved for full superusers
        restricted_permissions = [
            'add_logentry', 'delete_logentry', 'change_logentry',  # Example restricted actions
            'add_user', 'delete_user'  # Permissions that should remain for full superuser only
        ]
        all_permissions = Permission.objects.exclude(
            content_type__app_label='auth', codename__in=restricted_permissions
        )
        instance.user_permissions.set(all_permissions)
    elif not instance.is_limited_superuser:
        # Clear permissions if not a limited superuser
        instance.user_permissions.clear()


  #SCHOOL APP
  
class School(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_account_active = models.BooleanField(default=True, verbose_name='Status') # this track activation status
    # Add any other school-specific fields here
  
    def __str__(self):
      return self.name
  
# models.py
class SchoolQuerySet(models.QuerySet):
    def for_school(self, school):
        return self.filter(school=school)

class Student(models.Model):
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    objects = SchoolQuerySet.as_manager()
    def __str__(self):
      return self.name


class StaffProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)  # Allow null
    
    @admin.display(
      boolean = False,
      description = "Full name",
    )
    def full_name(self):
      return f"{self.user.first_name} {self.user.last_name}"
    def __str__(self):
      return f"{self.user.first_name} {self.user.last_name}"
# Extend User model to have easy access to UserProfile
CustomUser.profile = property(lambda u: StaffProfile.objects.get_or_create(user=u)[0])