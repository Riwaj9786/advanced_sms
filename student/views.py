from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from student.models import Student, ProgramCourse, Course, Semester, User, Program, Marks, Assignment, Submission
from student.forms import RegisterForm, LoginForm, AssignmentForm
from django.contrib.auth.hashers import make_password
from datetime import datetime
from django.contrib import messages
from django.core.files.storage import FileSystemStorage

def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('students:staff_dashboard', pk=request.user.pk)
        elif request.user.is_student:
            return redirect('students:student_dashboard', pk=request.user.pk)
        else:
            return HttpResponse('You are not Authenticated')

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_staff:
                    login(request, user)
                    return redirect('students:staff_dashboard', pk=user.pk)
                elif user.is_student:
                    login(request, user)
                    return redirect('students:student_dashboard', pk=user.pk)
                else:
                    form.add_error(None, "User not Verified!")
            else:
                form.add_error(None, "Invalid Username and Password!")
        else:
            form.add_error(None, 'Form is not Valid!')
    else:
        form = LoginForm()

    return render(request, 'index.html', {'form': form})


def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            email = form.cleaned_data.get('email')
            date_of_birth = form.cleaned_data.get('date_of_birth')
            is_student = form.cleaned_data.get('is_student')
            user.password = make_password(form.cleaned_data['password'])

            if is_student:
                try:
                    student = Student.objects.get(email=email, date_of_birth=date_of_birth)
                    if student.user:
                        form.add_error(None, "This student is already linked to a user account.")
                    else:
                        user.is_student = True
                        user.save()
                        student.user = user
                        student.save()
                        return redirect('students:home')
                except Student.DoesNotExist:
                    form.add_error(None, "No student found with the provided details.")
            else:
                user.is_staff = True
                user.save()
                return redirect('students:home')
    else:
        form = RegisterForm()

    return render(request, 'registration/signup.html', {'form': form})

@login_required
def staff_dashboard(request, pk):
    teacher = get_object_or_404(User, pk=pk)
    program_courses = ProgramCourse.objects.filter(teacher=teacher)

    if teacher != request.user:
        return HttpResponseForbidden("You are not authorized!")

    if teacher.is_superuser:
        students = Student.objects.all().order_by('-batch_year', 'first_name')
        student_count = students.count()
        users = User.objects.all().order_by('first_name')
        user_count = users.count()
        program_count = Program.objects.all().count()

        return render(request, 'staff/staff_dashboard.html', {
            'students': students,
            'users': users,
            'student_count': student_count,
            'user_count': user_count,
            'pc_count': program_count
        })

    students = Student.objects.filter(semester__programcourse__in=program_courses).distinct()
    student_count = students.count()
    program_count = program_courses.count()

    return render(request, 'staff/staff_dashboard.html', {
        'user': teacher,
        'student_count': student_count,
        'pc_count': program_count,
    })

@login_required
def student_dashboard(request, pk):
    student_user = get_object_or_404(User, pk=pk)
    student = Student.objects.get(user=student_user)

    if student_user != request.user:
        return HttpResponseForbidden("You are not Authorized!")

    return render(request, 'student/student_dashboard.html', {
        'student': student,
        'user': student_user
    })

@login_required
def user_logout(request):
    logout(request)
    return redirect('students:home')

@login_required
def student_lists(request, pk):
    teacher = get_object_or_404(User, pk=pk)
    program_courses = ProgramCourse.objects.filter(teacher=teacher)

    if teacher != request.user:
        return HttpResponseForbidden("You are not authorized!")

    course = request.GET.get('course')
    students = Student.objects.filter(semester__programcourse__in=program_courses).distinct()

    if course:
        students = students.filter(semester__programcourse__course__course_name=course)

    distinct_programs = program_courses.values_list('program__program_name', flat=True).distinct()
    distinct_courses = program_courses.values_list('course__course_name', flat=True).distinct()
    distinct_semesters = program_courses.values_list('semester__semester', flat=True).distinct()

    context = {
        'teacher': teacher,
        'students': students,
        'program_courses': program_courses,
        'programs': distinct_programs,
        'semesters': distinct_semesters,
        'courses': distinct_courses,
    }

    return render(request, 'staff/student_list.html', context)

@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)

    return render(request, 'student/student_detail.html', {'student': student})

@login_required
def classes_view(request, pk):
    teacher = get_object_or_404(User, pk=pk)
    program_courses = ProgramCourse.objects.filter(teacher=teacher)

    if teacher != request.user:
        return HttpResponseForbidden("You are not authorized!")

    return render(request, 'staff/classes.html', {
        'teacher': teacher,
        'program_courses': program_courses
    })

@login_required
def assignments(request, pk):
    teacher = get_object_or_404(User, pk=pk)

    if teacher != request.user:
        return HttpResponseForbidden("You are not authorized!")

    program_courses = ProgramCourse.objects.filter(teacher=teacher)
    assignments = Assignment.objects.filter(assigned_class__teacher=teacher, deadline__gte=datetime.now())
    inactive_assignments = Assignment.objects.filter(
        assigned_class__in=program_courses,
        deadline__lte=datetime.now()
    ).order_by('-deadline')

    if request.method == 'POST':
        form = AssignmentForm(request.POST, teacher=teacher)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.assigned_class = form.cleaned_data['assigned_class']
            assignment.created_by = request.user
            assignment.save()
            return redirect('students:assignments', pk=teacher.pk)
    else:
        form = AssignmentForm(teacher=teacher)

    return render(request, 'staff/assignment.html', {
        'teacher': teacher,
        'program_courses': program_courses,
        'form': form,
        'assignments': assignments,
        'inactive_assignments': inactive_assignments
    })

@login_required
def delete_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    assignment.delete()

    return redirect('students:assignments', pk=request.user.pk)

@login_required
def student_assignment_view(request):
    user = request.user

    if user.is_student:
        student = Student.objects.get(user=user)
        program_course = ProgramCourse.objects.filter(program=student.program, semester=student.semester)
        assignments = Assignment.objects.filter(
            assigned_class__in=program_course,
            deadline__gte=datetime.now()
        ).order_by('deadline')
        inactive_assignments = Assignment.objects.filter(
            assigned_class__in=program_course,
            deadline__lte=datetime.now()
        ).order_by('-deadline')

    return render(request, 'student/assignment.html', {
        'assignments': assignments,
        'inactive_assignments': inactive_assignments
    })

@login_required
def assignment_view(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    if request.method == "POST":
        if assignment.accepted_file_type == "pdf":
            if 'file' in request.FILES:
                file = request.FILES['file']
                submission = Submission.objects.create(
                    assignment=assignment,
                    student=request.user,
                    file=file,
                    submitted_at=datetime.now()
                )
                submission.save()
                messages.success(request, "Your PDF assignment has been submitted successfully!")
                return redirect('students:student_assignments')
            else:
                messages.error(request, "Please upload a valid PDF file.")

        elif assignment.accepted_file_type == "text":
            text_content = request.POST.get('text')
            if text_content:
                file_name = f"{request.user.username}_assignment_{assignment.pk}.txt"
                file_path = f"submissions/{file_name}/"
                fs = FileSystemStorage()
                with fs.open(file_path, 'w') as f:
                    f.write(text_content)

                submission = Submission.objects.create(
                    assignment=assignment,
                    student=request.user,
                    file=file_path,
                    submitted_at=datetime.now()
                )
                submission.save()
                messages.success(request, "Your Assignment has been submitted successfully!")
                return redirect('students:student_assignments')
            else:
                messages.error(request, "Please enter the text for your assignment.")

    return render(request, 'student/assignment_view.html', {'assignment': assignment})

@login_required
def submission_view(request, pk):
    user = request.user
    if user.is_staff:
        assignment = get_object_or_404(Assignment, pk=pk)
        submissions = Submission.objects.filter(assignment=assignment)

        return render(request, 'staff/submission_view.html', {
            'assignment': assignment,
            'submissions': submissions
        })

    else:
        return HttpResponse("You are not authorized!")



def session_expired(request):
    return render(request, 'session_expire.html')



@login_required
def marks_page(request, course_id, semester_id):
    try:
        course = Course.objects.get(id=course_id)
        semester = Semester.objects.get(id=semester_id)
        students = Student.objects.filter(programcourse__course=course, semester=semester)
    except (Course.DoesNotExist, Semester.DoesNotExist):
        messages.error(request, "Invalid course or semester")
        return redirect('some_error_page')  # Redirect to an error page or similar

    if request.method == 'POST':
        for student in students:
            marks_obtained = request.POST.get(f'marks_{student.id}')
            max_marks = request.POST.get(f'max_marks_{student.id}')
            if marks_obtained and max_marks:
                # Validate and create or update the marks entry
                Marks.objects.update_or_create(
                    student=student,
                    course=course,
                    defaults={'marks_obtained': marks_obtained, 'max_marks': max_marks}
                )
        messages.success(request, "Marks updated successfully")
        return redirect('marks_page', course_id=course_id, semester_id=semester_id)

    return render(request, 'marks_page.html', {'course': course, 'semester': semester, 'students': students})
