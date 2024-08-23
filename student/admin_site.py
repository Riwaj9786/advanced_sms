from django.contrib.admin.sites import AdminSite
from django.urls import path
from django.shortcuts import render

class CustomAdminSite(AdminSite):
    site_header = 'edu-sanchal: Admin Portal'
    site_title = 'edu-ikshya: School of Engineering'
    index_title = 'Welcome to the Admin Portal'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('myapp/', self.admin_view(self.my_custom_view), name='my_custom_view'),
        ]
        return custom_urls + urls

    def my_custom_view(self, request):
        context = {
            'title': 'My Custom View',
        }
        return render(request, 'admin/my_custom_template.html', context)

custom_admin_site = CustomAdminSite(name='custom_admin')
