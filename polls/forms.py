from django import forms
from .models import School,Student, CustomUser

# forms.py
class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['name', 'address', 'contact_email']


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'age']  # default fields

    def __init__(self, *args, **kwargs ):
        user = kwargs.pop('user', None)  # Get the user from the kwargs
        super(StudentForm, self).__init__(*args, **kwargs)

        if user and user.is_limited_superuser:
            self.fields['school'] = forms.ModelChoiceField(queryset=School.objects.all(), required=True,  label='School')  # Add the 'school' field for superusersr


