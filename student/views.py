from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from student.models import Student, ProgramCourse, User, Program, Assignment
from student.forms import RegisterForm, LoginForm, AssignmentForm
from django.contrib.auth.hashers import make_password


def home(request):
    # Check if the user is already authenticated
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
                    # Retrieve the student based on email and date of birth
                    student = Student.objects.get(email=email, date_of_birth=date_of_birth)
                    
                    # Ensure the student is not already linked to a user
                    if student.user:
                        form.add_error(None, "This student is already linked to a user account.")
                    else:
                        user.is_student = True
                        user.save()

                        # Link the user to the student
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
                
        return render(request, 'staff/staff_dashboard.html', {'students': students,
                                                              'users': users,
                                                              'student_count': student_count,
                                                              'user_count': user_count,
                                                              'pc_count': program_count})

    # Get the students associated with the semesters taught by the teacher
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
    
    return render(request, 'student/student_dashboard.html', {'student': student,
                                                              'user': student_user})


@login_required
def user_logout(request):
    logout(request)
    return redirect('students:home')


@login_required
def student_lists(request, pk):
    teacher = get_object_or_404(User, pk=pk)
    program_courses = ProgramCourse.objects.filter(teacher=teacher)

    # Authorization check
    if teacher != request.user:
        return HttpResponseForbidden("You are not authorized!")

    # Get filter values from the request
    program = request.GET.get('program')
    course = request.GET.get('course')
    semester = request.GET.get('semester')

    # Base queryset for students
    students = Student.objects.filter(semester__programcourse__in=program_courses).distinct()

    # Apply filters if they are provided
    if course:
        students = students.filter(semester__programcourse__course__course_name=course)

    # Get distinct values for filters
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

    # Authorization check
    if teacher != request.user:
        return HttpResponseForbidden("You are not authorized!")
    
    return render(request, 'staff/classes.html', {'teacher': teacher,
                                                  'program_courses': program_courses})


@login_required
def assignments(request, pk):
    teacher = get_object_or_404(User, pk=pk)
    
    if teacher != request.user:
        return HttpResponseForbidden("You are not authorized!")
    
    program_courses = ProgramCourse.objects.filter(teacher=teacher)
    assignments = Assignment.objects.filter(assigned_class__teacher=teacher)

    if request.method == 'POST':
        form = AssignmentForm(request.POST, teacher=teacher)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.assigned_class = form.cleaned_data['assigned_class']
            assignment.created_by = request.user  # Assign the current user as the creator
            assignment.save()
            return redirect('students:assignments', pk=teacher.pk)
    else:
        form = AssignmentForm(teacher=teacher)

    return render(request, 'staff/assignment.html', {
        'teacher': teacher,
        'program_courses': program_courses,
        'form': form,
        'assignments': assignments
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
        assignments = Assignment.objects.filter(assigned_class__in=program_course).order_by('deadline')

        return render(request, 'student/assignment.html', {'assignments':assignments})


@login_required
def assignment_view(request, pk):
        assignment = get_object_or_404(Assignment, pk=pk)

        return render(request, 'student/assignment_view.html', {'assignment': assignment})



def session_expired(request):
    return render(request, 'session_expire.html')