"""
URL configuration for leavemanagementsystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from app1 import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),
    path('home', views.home, name='home'),

    path('admin@reg_ster', views.adminreg, name='adminreg'),
    path('admin_login', views.admin_login, name='admin_login'),
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('adminlogout', views.adminlogout, name='adminlogout'),

    path('admin_change_creds', views.admin_change_creds, name='admin_change_creds'),

    path('add_department', views.add_department, name='add_department'),
    path('manage_department', views.manage_department, name='manage_department'),
    path('update_department/<int:id>/', views.update_department, name='update_department'),
    path('delete_department/<int:id>/', views.delete_department, name='delete_department'),

    path('add_leave_type', views.add_leave_type, name='add_leave_type'),
    path('manage_leavetypes', views.manage_leavetypes, name='manage_leavetypes'),
    path('update_leave_type/<int:id>/', views.update_leave_type, name='update_leave_type'),
    path('delete_leavetypes/<int:id>/', views.delete_leavetypes, name='delete_leavetypes'),

    path('add_employee', views.add_employee, name='add_employee'),
    path('manage_emp', views.manage_emp, name='manage_emp'),
    path('update_emp/<int:id>/', views.update_emp, name='update_emp'),
    path('delete_emp/<int:id>/', views.delete_emp, name='delete_emp'),

    path('emp_dashboard', views.emp_dashboard, name='emp_dashboard'),
    path('emp_login', views.emp_login, name='emp_login'),
    path('emplogout', views.emplogout, name='emplogout'),

    path('emp_change_creds', views.emp_change_creds, name='emp_change_creds'),
    path('error/', views.error, name='error'),

    path('appy_leave', views.appy_leave, name='appy_leave'),
    path('leave_status', views.leave_status, name='leave_status'),

    path('admin_leaves', views.admin_leaves, name='admin_leaves'),
    path('accept_leave/<int:id>/', views.accept_leave, name='accept_leave'),
    path('reject_leave/<int:id>/', views.reject_leave, name='reject_leave'),

    path('accepted_leaves', views.accepted_leaves, name='accepted_leaves'),
    path('reject_modify/<int:id>/', views.reject_modify, name='reject_modify'),

    path('reject_leaves', views.reject_leaves, name='reject_leaves'),
    path('accept_modify/<int:id>/', views.accept_modify, name='accept_modify'),

    path('all_leaves', views.all_leaves, name='all_leaves'),

    ]
