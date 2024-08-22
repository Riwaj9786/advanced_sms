from django.urls import path
from student import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'students'

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='user_register'),
    path('accounts/login/', views.session_expired, name='session_expired'),
    path('students/', views.total_students, name='total_students'),

    # Views for Staff
    path('staff/<pk>/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/students/<pk>/', views.student_lists, name='student_lists'),
    path('staff/classes/<pk>/', views.classes_view, name='classes_view'),
    path('staff/assignments/<pk>/', views.assignments, name='assignments'),
    path('staff/assignments/<pk>/delete/', views.delete_assignment, name='delete_assignment'),
    path('staff/student/<pk>/', views.student_detail, name='student_detail'),
    path('staff/assignments/<pk>/submissions/', views.submission_view, name='submission_view'),
    path('marks/<pk>/', views.marks_dashboard, name='marks_dashboard'),
    path('marks/<course_id>/<program_id>/<semester_id>/', views.marking_page, name='marking_page'),

    #Views for student
    path('student/dashboard/<pk>/', views.student_dashboard, name='student_dashboard'),
    path('student/assignments/', views.student_assignment_view, name="student_assignments"),
    path('student/assignment/<pk>/', views.assignment_view, name="assignment_view"),

    path('staff/assignments/<pk>/check_plagiarism/', views.check_plagiarism, name='check_plagiarism'), # todo
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
