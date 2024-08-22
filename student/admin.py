from django.contrib import admin
from .models import User, Program, Student, Submission, Plagiarism, Course, ProgramCourse, Marks
from .admin_site import custom_admin_site  # Import from the correct location
from django import forms

class ProgramCourseForm(forms.ModelForm):
    class Meta:
        model = ProgramCourse
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = User.objects.filter(is_staff=True)

class ProgramCourseAdmin(admin.ModelAdmin):
    form = ProgramCourseForm

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_student')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset

custom_admin_site.register(User, CustomUserAdmin)
custom_admin_site.register(Program)
custom_admin_site.register(Student)
custom_admin_site.register(Course)
custom_admin_site.register(Marks)
custom_admin_site.register(Submission)
custom_admin_site.register(Plagiarism)
custom_admin_site.register(ProgramCourse, ProgramCourseAdmin)
