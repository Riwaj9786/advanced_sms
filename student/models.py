import uuid
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils.text import slugify

class Program(models.Model):
    program_id = models.CharField(max_length=12, unique=True)
    program_name = models.CharField(max_length=60)

    def __str__(self):
        return self.program_name


class Semester(models.Model):
    SEMESTER_CHOICES = [
        ('I', 'I'),
        ('II', 'II'),
        ('III', 'III'),
        ('IV', 'IV'),
        ('V', 'V'),
        ('VI', 'VI'),
        ('VII', 'VII'),
        ('VIII', 'VIII'),
    ]

    semester_id = models.CharField(max_length=4, unique=True)
    semester = models.CharField(max_length=5, choices=SEMESTER_CHOICES)

    def __str__(self):
        return self.semester



class User(AbstractUser):
    user_id = models.CharField(max_length=15, unique=True, editable=False)
    address = models.CharField(max_length=150, null=True, blank=False)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    is_staff = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = str(uuid.uuid4())[:15]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username




class Student(models.Model):
    registration_number = models.CharField(max_length=30, unique=True, editable=False)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=100)
    batch_year = models.CharField(max_length=4)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    date_of_birth = models.DateField()
    email = models.EmailField(blank=True, null=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.RESTRICT)
    user = models.OneToOneField(User, on_delete=models.RESTRICT, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        if not self.registration_number:

            # Generate registration number based on faculty code, batch year, and student count
            count = Student.objects.filter(program=self.program, batch_year=self.batch_year).count() + 1
            registration_number = f"{self.batch_year}-{self.program.pk}-{count}"
            self.registration_number = slugify(registration_number)  # Generate a slug from the registration number
        
        super().save(*args, **kwargs)


class Course(models.Model):
    course_id = models.CharField(max_length=15, unique=True)
    course_name = models.CharField(max_length=150)

    def __str__(self):
        return self.course_name


class ProgramCourse(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.program.program_name} - {self.course.course_name}"


class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=2, blank=True, null=True)

    def __str__(self):
        return f"{self.student.first_name or self.student.user.username} - {self.course.course_name}"



# Model for Assignment
class Assignment(models.Model):
    ACCEPTED_FILE_TYPES = [
        ('text', 'Text File'),
        ('pdf', 'PDF File'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    deadline = models.DateTimeField()
    worth = models.IntegerField()
    research_links = models.JSONField(blank=True, null=True)  # This field can store a list of URLs
    accepted_file_type = models.CharField(max_length=10, choices=ACCEPTED_FILE_TYPES)
    assigned_class = models.ForeignKey(ProgramCourse, on_delete=models.CASCADE, related_name='assignments')
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title



# Model for Submission
class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='files/submissions/')
    text = models.TextField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_checked = models.BooleanField(default=False)  # To mark if the submission has been checked for plagiarism

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"