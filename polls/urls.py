from django.urls import path, include
from . import views
from django.conf.urls import handler404


app_name = 'polls'
handler404 = views.custom_404_view
urlpatterns = [
        path('add_school', views.add_school, name='add_school'),
        path('add_student', views.add_student, name='add_student'),
        path('student_list', views.student_list, name='student_list'),
  ]