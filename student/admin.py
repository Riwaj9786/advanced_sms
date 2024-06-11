from django.contrib import admin
from .models import User, Assignment, Program, Semester, Student, Course, ProgramCourse, Marks

admin.site.register(User)
admin.site.register(Program)
admin.site.register(Semester)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(ProgramCourse)
admin.site.register(Marks)
admin.site.register(Assignment)
