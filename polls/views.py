from django.shortcuts import render, redirect, get_object_or_404
from .models import School, Student
from .forms import SchoolForm, StudentForm
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.conf import settings



def custom_404_view(request, exception):
    return render(request, '404.html', status=404)
    
@login_required
@user_passes_test(lambda u: u.is_limited_superuser)
def add_school(request):
    if request.method == "POST":
        form = SchoolForm(request.POST)
        if form.is_valid():
            school = form.save()
            # Optional: Assign the new school to the user if needed
            # UserProfile.objects.create(user=request.user, school=school)
            return redirect(settings.LOGIN_URL)  # Redirect to a list of schools
    else:
        form = SchoolForm()
    return render(request, 'polls/add_school.html', {'form': form})


@login_required
@permission_required('polls.add_student', raise_exception=True)  # Replace 'app_name' with your app name
def add_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST, user=request.user)
        if form.is_valid():
            student = form.save(commit=False)
            if request.user.is_limited_superuser:
              student.school = form.cleaned_data['school']
            else:
              student.school = request.user.profile.school  # Automatically set the school
            student.save()
            return redirect(settings.LOGIN_URL)  # Redirect after saving
    else:
        form = StudentForm(user=request.user)
    return render(request, 'polls/add_student.html', {'form': form})


@login_required
def student_list(request):
    if request.current_school:
        #students = Student.objects.filter(school=request.current_school)
        students = Student.objects.for_school(request.current_school)
    else:
        students = Student.objects.none()  # No access if no school context
    return render(request, 'polls/student_list.html', {'students': students})