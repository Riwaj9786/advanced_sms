from django.urls import path
from student import views

app_name = 'students'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.user_register, name='user_register'),
    path('staff/<pk>/', views.staff_dashboard, name='staff_dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('students/<pk>/', views.student_lists, name='student_lists'),
    path('classes/<pk>/', views.classes_view, name='classes_view'),
    path('assignments/<pk>/', views.assignments, name='assignments'),
    path('assignments/<pk>/delete/', views.delete_assignment, name='delete_assignment'),
    path('staff/student/<pk>/', views.student_detail, name='student_detail'),
    path('student/<pk>/', views.student_dashboard, name='student_dashboard'),
]
