from django.urls import path
from student import views

app_name = 'students'

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='user_register'),
    path('accounts/login/', views.session_expired, name='session_expired'),

    # Views for Staff
    path('staff/<pk>/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/students/<pk>/', views.student_lists, name='student_lists'),
    path('staff/classes/<pk>/', views.classes_view, name='classes_view'),
    path('staff/assignments/<pk>/', views.assignments, name='assignments'),
    path('staff/assignments/<pk>/delete/', views.delete_assignment, name='delete_assignment'),
    path('staff/student/<pk>/', views.student_detail, name='student_detail'),

    #Views for student
    path('student/dashboard/<pk>/', views.student_dashboard, name='student_dashboard'),
    path('student/assignments/', views.student_assignment_view, name="student_assignments"),
    path('student/assignment/<pk>/', views.assignment_view, name="assignment_view"),
]
