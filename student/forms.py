from django import forms
from student.models import User, Assignment, ProgramCourse, Student
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

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
    email_address = forms.CharField(max_length=30, required=True)
    date_of_birth = forms.DateField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def clean(self):
        cleaned_data = super().clean()
        registration_number = cleaned_data.get('registration_number')
        date_of_birth = cleaned_data.get('date_of_birth')
        program = cleaned_data.get('program')

        if not Student.objects.filter(registration_number=registration_number, date_of_birth=date_of_birth, program=program).exists():
            raise forms.ValidationError("No student found with the provided details.")
        return cleaned_data