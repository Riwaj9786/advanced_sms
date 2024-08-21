from django.contrib.admin import AdminSite

class CustomAdminSite(AdminSite):
    site_header = 'Edu-Ikshya: Admin Portal'
    site_title = 'Edu-Ikshya Admin'
    index_title = 'Welcome to the Edu-Ikshya Admin Portal'

custom_admin_site = CustomAdminSite(name='custom_admin')