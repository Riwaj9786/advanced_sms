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
from django.urls import reverse

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
def total_students(request):
    user = request.user
    if user.is_superuser:
        # Order students by registration number (descending) and then by first name (ascending)
        students = Student.objects.all().order_by('registration_number', 'first_name')
    else:
        # Redirect non-superuser with an error message
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')  # Replace 'home' with the name of the page to redirect to

    return render(request, 'staff/students.html', {
        'students': students,
    })



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
    semester = request.GET.get('semester')
    students = Student.objects.filter(semester__programcourse__in=program_courses).distinct().order_by('registration_number')

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

    return render(request, 'staff/student_detail.html', {'student': student})

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

        # Check which assignments have been submitted by the student
        submissions = Submission.objects.filter(student=user, assignment__in=assignments)
        submission_status = {
            assignment.pk: submissions.filter(assignment=assignment).exists()
            for assignment in assignments
        }

        return render(request, 'student/assignment.html', {
            'assignments': assignments,
            'inactive_assignments': inactive_assignments,
            'submission_status': submission_status
        })

    else:
        # Handle non-student users
        messages.error(request, "You do not have permission to view this page.")
        return redirect('home')


@login_required
def assignment_view(request, pk):
    if request.user.is_student:
        assignment = get_object_or_404(Assignment, pk=pk)
        submission, created = Submission.objects.get_or_create(assignment=assignment, student=request.user)

        if request.method == "POST":
            if assignment.accepted_file_type == "pdf":
                if 'file' in request.FILES:
                    file = request.FILES['file']
                    # Replace existing file if already submitted
                    if submission.file and submission.file.name != file.name:
                        # Delete the old file
                        fs = FileSystemStorage()
                        fs.delete(submission.file.name)
                    submission.file = file
                    submission.submitted_at = datetime.now()
                    submission.is_submitted = True
                    submission.is_checked = True
                    submission.save()
                    messages.success(request, "Your PDF assignment has been submitted successfully!")
                    return redirect('students:assignment_view',)
                else:
                    messages.error(request, "Please upload a valid PDF file.")

            elif assignment.accepted_file_type == "text":
                text_content = request.POST.get('text')
                if text_content:
                    file_name = f"{request.user.username}_assignment_{assignment.pk}.txt"
                    file_path = f"submissions/{file_name}/"
                    fs = FileSystemStorage()

                    # Replace existing text file if already submitted
                    if submission.file and submission.file.name != file_path:
                        # Delete the old file
                        fs.delete(submission.file.name)

                    with fs.open(file_path, 'w') as f:
                        f.write(text_content)

                    submission.file = file_path
                    submission.submitted_at = datetime.now()
                    submission.is_submitted = True
                    submission.is_checked = True
                    submission.save()
                    messages.success(request, "Your Assignment has been submitted successfully!")
                    return redirect('students:student_assignments')
                else:
                    messages.error(request, "Please enter the text for your assignment.")

        return render(request, 'student/assignment_view.html', {'assignment': assignment, 'submission': submission})
    else:
        # Handle non-student users
        messages.error(request, "You do not have permission to view this page.")
        return redirect('home')


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
def marks_dashboard(request, pk):
    teacher = get_object_or_404(User, pk=pk)
    program_courses = ProgramCourse.objects.filter(teacher=teacher)

    if teacher != request.user:
        return HttpResponseForbidden("You are not authorized!")

    return render(request, 'staff/marks_dashboard.html', {
        'teacher': teacher,
        'program_courses': program_courses
    })


@login_required
def marking_page(request, program_id, course_id, semester_id):
    marks_dict = {}

    # Retrieve the specific course, program, and semester
    course = get_object_or_404(Course, course_id=course_id)
    program = get_object_or_404(Program, program_id=program_id)
    semester = get_object_or_404(Semester, semester_id=semester_id)

    # Retrieve the ProgramCourse for the given course, program, and semester
    program_course = get_object_or_404(ProgramCourse, program=program, course=course, semester=semester)

    # Filter students who are enrolled in the specific course and semester
    students = Student.objects.filter(program=program, semester=semester).distinct().order_by('first_name')

    # Initialize marks dictionary for each student
    for student in students:
        marks = Marks.objects.filter(course=course, student=student).first()
        marks_dict[student.id] = marks.marks_obtained if marks else None

    if request.method == 'POST':
        errors = []
        if 'submit_all' in request.POST:
            for student in students:
                marks_value = request.POST.get(f'marks_{student.id}')
                if marks_value:
                    try:
                        marks_value = float(marks_value)
                        if 0 <= marks_value <= 50:
                            mark_entry, created = Marks.objects.get_or_create(
                                student=student,
                                course=course,
                                defaults={'marks_obtained': marks_value, 'max_marks': 50.00}
                            )
                            if not created:
                                mark_entry.marks_obtained = marks_value
                                mark_entry.save()
                        else:
                            errors.append(f"Marks for {student.first_name} {student.last_name} must be between 0 and 50.")
                    except ValueError:
                        errors.append(f"Invalid marks value for {student.first_name} {student.last_name}.")

            if not errors:
                messages.success(request, 'All marks have been updated successfully.')
            else:
                for error in errors:
                    messages.error(request, error)

        else:
            for student in students:
                if f'save_{student.id}' in request.POST:
                    marks_value = request.POST.get(f'marks_{student.id}')
                    if marks_value:
                        try:
                            marks_value = float(marks_value)
                            if 0 <= marks_value <= 50:
                                mark_entry, created = Marks.objects.get_or_create(
                                    student=student,
                                    course=course,
                                    defaults={'marks_obtained': marks_value, 'max_marks': 50.00}
                                )
                                if not created:
                                    mark_entry.marks_obtained = marks_value
                                    mark_entry.save()
                                messages.success(request, f'Marks for {student.first_name} {student.last_name} saved successfully.')
                            else:
                                errors.append(f"Marks for {student.first_name} {student.last_name} must be between 0 and 50.")
                        except ValueError:
                            errors.append(f"Invalid marks value for {student.first_name} {student.last_name}.")
                    
            if not errors:
                messages.success(request, 'Marks have been updated successfully.')
            else:
                for error in errors:
                    messages.error(request, error)

        return redirect('students:marking_page', course_id=course_id, program_id=program_id, semester_id=semester_id)

    # Annotate students with their marks
    students_with_marks = []
    for student in students:
        marks_obtained = marks_dict.get(student.id, None)
        students_with_marks.append({
            'student': student,
            'marks_obtained': marks_obtained
        })

    return render(request, 'staff/marking_page.html', {
        'course': course,
        'students_with_marks': students_with_marks,
        'program_course': program_course,
    })
