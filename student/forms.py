from django import forms
from student.models import User, Assignment, ProgramCourse, Student
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'is_student', 'date_of_birth']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match")

        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'deadline', 'worth', 'research_links', 'accepted_file_type', 'assigned_class']

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields['assigned_class'].queryset = ProgramCourse.objects.filter(teacher=teacher)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['deadline'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})



class StudentRegistrationForm(UserCreationForm):
    date_of_birth = forms.DateField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean(self):
        cleaned_data = super().clean()
        date_of_birth = cleaned_data.get('date_of_birth')
        email = cleaned_data.get('email')

        if not Student.objects.filter(email=email, date_of_birth=date_of_birth).exists():
            raise forms.ValidationError("No student found with the provided details.")
        return cleaned_data