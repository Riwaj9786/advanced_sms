from django.contrib import admin
from django.urls import path

from .views import model_form_upload

app_name = 'plagiarism'

urlpatterns = [
    path('plagiarism-check/', model_form_upload, name='plagiarism_checker'),
]
