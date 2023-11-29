from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from .models import admindata, department, emp, leavetypes, leaves
from django.http import HttpResponse
from django.contrib.auth.views import LoginView
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import get_object_or_404,redirect
from django.templatetags.static import static
from datetime import date

from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.middleware.csrf import CsrfViewMiddleware
from django.db.utils import IntegrityError, OperationalError
from django.http import JsonResponse
from django.db import transaction
import re
from django.contrib.auth.models import Group
from django.contrib import messages

import os


manager_group, _ = Group.objects.get_or_create(name='manager')

# Create the "employee" group
employee_group, _ = Group.objects.get_or_create(name='employee')

def home(request):
    return render(request, 'home.html')




def adminreg(request):
    success_message = None
    error_message = None
    error_message_password = ""
    error_message_confirm = ""
    error_message_admin_exist = ""


    if request.method == 'POST':
        try:


            admin_id = request.POST['admin_id']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            mobile_number = request.POST['mobile_number']
            username = request.POST['username']
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']

            # Perform field validations
            admindata.mobile_number_validator(mobile_number)
            pattern = re.compile(r'^([a-zA-Z]{2,5}\d{3,5})$')

            if not pattern.match(admin_id):
                error_message_adminid = 'Admin ID must be in the alpha(2-5)+numeric(3-5) format'
                return render(request, 'adminreg.html', {'error_message_adminid': error_message_adminid})
            # Check if admin_id is already used
            if admindata.objects.filter(admin_id=admin_id).exists():
                error_message_admin_exist = 'This Admin ID is already in use.'
                return render(request, 'adminreg.html', {'error_message_admin_exist':error_message_admin_exist})
            # Check if the username already exists
            if User.objects.filter(username=username).exists():
                error_message_username = 'This username is already in use. Try a different one.'
                return render(request, 'adminreg.html', {'error_message_username':error_message_username})
            else:
                # Perform password validation
                if not (len(password) >= 8 and any(c.isupper() for c in password) and any(c.isdigit() for c in password) and any(c in "!@#$%^&*" for c in password)):
                    error_message_password = "Password must contain at least 8 characters. At least one uppercase character.At least one special character,and at least one number."
                # Check if password and confirm_password match
                elif password != confirm_password:
                    error_message_confirm = "Password and confirm password do not match."
                else:
                    # All validations passed, create User and admindata objects
                    # Assign a user to the "manager" group
                    user = User.objects.create_user(username=username, password=password, email=email)
                    # Assign the user to the "manager" group
                    user.groups.add(manager_group)
                    admindata.objects.create(
                        admin_id=admin_id,
                        first_name=first_name.title(),
                        last_name=last_name.title(),
                        email=email,
                        mobile_number=mobile_number,
                        username = username
                    )
                    success_message = 'Data added successfully.'


        except IntegrityError as I:
            error_message = 'An error occurred while saving to the database. Please try again later.'
        except OperationalError as O:
            error_message = 'Database connection error. Please check your database server.'

    return render(request, 'adminreg.html', {
        'success_message': success_message,
        'error_message': error_message,
        'error_message_password': error_message_password,
        'error_message_confirm': error_message_confirm,
        'error_message_admin_exist': error_message_admin_exist
    })

def admin_dashboard(request):
    pending_leaves_count = leaves.objects.filter(Status='pending').count()
    accepted_leaves_count = leaves.objects.filter(Status='accepted').count()
    rejected_leaves_count = leaves.objects.filter(Status='rejected').count()
    all_app_count = leaves.objects.all().count()

    context = {
        'pending_count': pending_leaves_count,
        'accepted_count': accepted_leaves_count,
        'rejected_count': rejected_leaves_count,
        'all_app_count': all_app_count,
    }
    return render(request, 'admin_dashboard.html', context)

def accepted_leaves(request):
    error_messages=""

    try:
        # Filter the leaves queryset to include only records with Status 'pending'
        data = leaves.objects.filter(Status='accepted')
    except OperationalError as oe:
        error_messages = 'Database connection error. Please check your database server: {}'.format(oe)

    except IntegrityError as e:
        # IntegrityError occurred
        error_messages = 'An integrity error occurred while authenticating. Please try again later.'

    return render(request, 'accepted_leaves.html', {'data': data, 'error_messages':error_messages})

def reject_modify(request, id):
    # Your logic to reject a leave
    # Example: Change the status of the leave to 'rejected'
    leave = leaves.objects.get(pk=id)
    leave.Status = 'rejected'
    leave.save()
    return redirect('accepted_leaves')  # Redirect to the admin leaves page

def reject_leaves(request):
    error_messages=""

    try:
        # Filter the leaves queryset to include only records with Status 'pending'
        data = leaves.objects.filter(Status='rejected')
    except OperationalError as oe:
        error_messages = 'Database connection error. Please check your database server: {}'.format(oe)

    except IntegrityError as e:
        # IntegrityError occurred
        error_messages = 'An integrity error occurred while authenticating. Please try again later.'

    return render(request, 'reject_leaves.html', {'data': data, 'error_messages':error_messages})

def accept_modify(request, id):
    # Your logic to reject a leave
    # Example: Change the status of the leave to 'rejected'
    leave = leaves.objects.get(pk=id)
    leave.Status = 'accepted'
    leave.save()
    return redirect('reject_leaves')  # Redirect to the admin leaves page

def all_leaves(request):
    error_messages=""

    try:
        # Filter the leaves queryset to include only records with Status 'pending'
        data = leaves.objects.all()
    except OperationalError as oe:
        error_messages = 'Database connection error. Please check your database server: {}'.format(oe)

    except IntegrityError as e:
        # IntegrityError occurred
        error_messages = 'An integrity error occurred while authenticating. Please try again later.'

    return render(request, 'all_leaves.html', {'data': data, 'error_messages':error_messages})


def admin_login(request):
    # Handle user login
    error_messages=""
    success_message=""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:

            #CsrfViewMiddleware().process_view(request, None, (), {})
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Check if the user belongs to the "manager" group
                if user.groups.filter(name='manager').exists():
                    login(request, user)
                    # User is a manager
                    # Do something for managers
                    request.session['username']=username
                    # Set a success message
                    success_message="Login successful. Welcome to the admin dashboard!"




                else:
                    # User is not in the "manager" group
                    error_message = 'This username or password is incorrect.'
                    # Handle as needed, you can redirect to the login page or render the login form with an error message
                    return render(request, 'admin_login.html', {'error_message': error_message})

            else:
                error_message = 'This username or password is incorrect.'
                # Handle as needed, you can redirect to the login page or render the login form with an error message
                return render(request, 'admin_login.html', {'error_message': error_message})

        except IntegrityError as e:
            # IntegrityError occurred
            error_messages = 'An integrity error occurred while authenticating. Please try again later.'
        except OperationalError as e:
            # OperationalError occurred
            error_messages = 'A database connection error occurred. Please check your database server.'

    # Render login form for GET request
    return render(request, 'admin_login.html',{'error_messages':error_messages, 'success_message':success_message})

def adminlogout(request):
    logout(request)
    return redirect('home')


@login_required
def admin_change_creds(request):
    error_messages = ""
    success_message = ""
    error_message_p = ""
    error_message_u = ""

    # Assuming that the logged-in user is in the "manager" group
    user = request.user

    if request.method == 'POST':
        try:
            # Validate CSRF token
            #CsrfViewMiddleware().process_view(request, None, (), {})

            old_password = request.POST['old_password']
            new_password = request.POST['new_password']
            confirm_new_password = request.POST['confirm_new_password']
            new_username = request.POST['new_username']

            # Validate old password
            if not user.check_password(old_password):
                error_message_p = "Old password is incorrect."
            elif new_password != confirm_new_password:
                error_message_p = "New password and confirm password do not match."
            elif not (len(new_password) >= 8 and any(c.isupper() for c in new_password) and any(c.isdigit() for c in new_password) and any(c in "!@#$%^&*" for c in new_password)):
                error_message_p = "New password must contain at least 8 characters, one uppercase character, one digit, and one special character."
            elif new_username != user.username and User.objects.filter(username=new_username).exists():
                error_message_u = 'This username is already in use. Try a different one.'
            else:
                # Update the username and password
                user.username = new_username
                user.set_password(new_password)
                user.save()

                admin_instance = admindata.objects.get(email = user.email)
                admin_instance.username = new_username
                admin_instance.save()

                # Log out the user
                logout(request)
                success_message = "Password and username updated successfully. Please log in again."
                # Redirect to the login page
                return redirect('admin_login')

        except OperationalError as oe:
            error_messages = 'Database connection error. Please check your database server: {}'.format(oe)

        except IntegrityError as e:
            # IntegrityError occurred
            error_messages = 'An integrity error occurred while authenticating. Please try again later.'

    return render(request, 'admin_change_creds.html', {
        'error_messages': error_messages,
        'error_message_p': error_message_p,
        'error_message_u': error_message_u,
    })


def add_department(request):
    success_message = ""
    error_messages = ""

    if request.method == 'POST':
        dep_name = request.POST['dep_name']
        dep_short_name = request.POST['dep_short_name']
        dep_code = request.POST['dep_code']

        try:
            if department.objects.filter(dep_name=dep_name).exists():
                error_messages_name = 'This Department Name is already in use.'
                return render(request, 'add_department.html', {'error_messages_name':error_messages_name})

            # Validate dep_short_name
            pattern_short_name = re.compile(r'^[A-Z]{2,5}$')
            if not pattern_short_name.match(dep_short_name):
                error_messages_short = 'Department Short Name should be in format like 2-5 uppercase letters.'
                return render(request, 'add_department.html', {'error_messages_short': error_messages_short})



            # Validate data based on the model conditions
            new_department = department(dep_name=dep_name, dep_short_name=dep_short_name, dep_code=dep_code)

            new_department.save()

            success_message = 'Department added successfully!'
            return render(request, 'add_department.html', {'success_message': success_message})

        except ValidationError as e:
            error_messages = 'Validation error. Please check your input.'

        except OperationalError as oe:
            error_messages = 'Database connection error. Please check your database server: ' + str(oe)

        except IntegrityError as e:
            if 'unique constraint' in str(e):
                error_messages = 'A department with the same name already exists.'
            else:
                error_messages = 'An integrity error occurred while adding the department. Please try again later.'

    return render(request, 'add_department.html', {'error_messages': error_messages})


def manage_department(request):
    try:
        data=department.objects.all()
        return render(request, 'manage_department.html', {'data':data })
    except OperationalError as O:
        error_message = 'Database connection error. Please check your database server.'
        return render(request, 'manage_department.html', {'error_message': error_message})
    return render(request, 'manage_department.html')



def update_department(request, id):
    success_message = ""
    error_messages = ""

    # Retrieve the department instance based on the provided ID
    existing_department = get_object_or_404(department, id=id)
    try:
        data = department.objects.get(id=id)
    except department.DoesNotExist:
        return HttpResponse("Department not found")

    if request.method == 'POST':
        dep_name = request.POST['dep_name']
        dep_short_name = request.POST['dep_short_name']
        dep_code = request.POST['dep_code']

        try:
            # Check if the updated department name already exists
            if dep_name != existing_department.dep_name and department.objects.filter(dep_name=dep_name).exists():
                error_messages_name = 'This Department Name is already in use.'
                return render(request, 'update_department.html', {'error_messages_name':error_messages_name, 'data':data})

            # Validate dep_short_name
            pattern_short_name = re.compile(r'^[A-Z]{2,5}$')
            if not pattern_short_name.match(dep_short_name):
                error_messages_short = 'Department Short Name should be in format like 2-5 uppercase letters.'
                return render(request, 'update_department.html', {'error_messages_short': error_messages_short, 'data':data})

            # Update the existing department instance
            existing_department.dep_name = dep_name
            existing_department.dep_short_name = dep_short_name
            existing_department.dep_code = dep_code

            existing_department.save()

            success_message = 'Department updated successfully!'
            return render(request, 'update_department.html', {'success_message': success_message, 'data':data})

        except ValidationError as e:
            error_messages = 'Validation error. Please check your input.'

        except OperationalError as oe:
            error_messages = 'Database connection error. Please check your database server: ' + str(oe)

        except IntegrityError as e:
            if 'unique constraint' in str(e):
                error_messages = 'A department with the same name already exists.'
            else:
                error_messages = 'An integrity error occurred while updating the department. Please try again later.'

    # Pass the existing department instance to the template for pre-filling the form
    return render(request, 'update_department.html', {'existing_department': existing_department, 'error_messages': error_messages, 'data':data})




def delete_department(request, id):
    data=department.objects.get(id=id)
    data.delete()

    return redirect('manage_department')



def add_leave_type(request):
    success_message = ""
    error_messages = ""

    if request.method == 'POST':
        leave_name = request.POST['leave_name']
        leave_code = request.POST['leave_code']
        description = request.POST['description']
        try:
            if leavetypes.objects.filter(leave_name=leave_name).exists():
                error_messages_name = 'This Leave Type is already in use.'
                return render(request, 'add_leave_type.html', {'error_messages_name':error_messages_name})

            # Validate data based on the model conditions
            new_leavetypes = leavetypes(leave_name=leave_name, leave_code=leave_code, description=description)

            new_leavetypes.save()

            success_message = 'Leave Type added successfully!'
            return render(request, 'add_leave_type.html', {'success_message': success_message})

        except ValidationError as e:
            error_messages = 'Validation error. Please check your input.'

        except OperationalError as oe:
            error_messages = 'Database connection error. Please check your database server: ' + str(oe)

        except IntegrityError as e:
            if 'unique constraint' in str(e):
                error_messages = 'A Leave Type with the same name already exists.'
            else:
                error_messages = 'An integrity error occurred while adding the department. Please try again later.'

    return render(request, 'add_leave_type.html', {'error_messages': error_messages})



def manage_leavetypes(request):
    try:
        data=leavetypes.objects.all()
        return render(request, 'manage_leavetypes.html', {'data':data })
    except OperationalError as O:
        error_message = 'Database connection error. Please check your database server.'
        return render(request, 'manage_leavetypes.html', {'error_message': error_message})
    return render(request, 'manage_leavetypes.html')




def update_leave_type(request, id):
    success_message = ""
    error_messages = ""

    # Retrieve the department instance based on the provided ID
    existing_leavetypes = get_object_or_404(leavetypes, id=id)
    try:
        data = leavetypes.objects.get(id=id)
    except leavetypes.DoesNotExist:
        return HttpResponse("Leave Types not found")

    if request.method == 'POST':
        leave_name = request.POST['leave_name']
        leave_code = request.POST['leave_code']
        description = request.POST['description']

        try:
            # Check if the updated department name already exists
            if leave_name != existing_leavetypes.leave_name and leavetypes.objects.filter(leave_name=leave_name).exists():
                error_messages_name = 'This Leave Type is already in use.'
                return render(request, 'update_leave_type.html', {'error_messages_name':error_messages_name, 'data':data})

            # Update the existing department instance
            existing_leavetypes.leave_name = leave_name
            existing_leavetypes.leave_code = leave_code
            existing_leavetypes.description = description

            existing_leavetypes.save()

            success_message = 'Leave Type updated successfully!'
            return render(request, 'update_leave_type.html', {'success_message': success_message, 'data':data})

        except ValidationError as e:
            error_messages = 'Validation error. Please check your input.'

        except OperationalError as oe:
            error_messages = 'Database connection error. Please check your database server: ' + str(oe)

        except IntegrityError as e:
            if 'unique constraint' in str(e):
                error_messages = 'A department with the same name already exists.'
            else:
                error_messages = 'An integrity error occurred while updating the department. Please try again later.'

    # Pass the existing department instance to the template for pre-filling the form
    return render(request, 'update_leave_type.html', {'existing_leavetypes': existing_leavetypes, 'error_messages': error_messages, 'data':data})




def delete_leavetypes(request, id):
    data=leavetypes.objects.get(id=id)
    data.delete()
    return redirect('manage_leavetypes')



def add_employee(request):
    success_message = ""
    error_messages = []

    # Assume dep_name is None by default
    dep_name = None
    dep_select_name = department.objects.all()

    if request.method == 'POST':
        emp_id = request.POST['emp_id']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        gender = request.POST['gender']
        dob = request.POST['dob']

        # Check if 'dep' key exists in the POST data
        dep_name = request.POST['dep']

        address = request.POST['address']
        city = request.POST['city']
        country = request.POST['country']
        mobile_number = request.POST['mobile_number']
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        try:
            pattern = re.compile(r'^([a-zA-Z]{2,5}\d{3,5})$')

            if not pattern.match(emp_id):
                error_message_emp_id = 'Employee ID must be in the alpha(2-5)-numeric(3-5) format'
                return render(request, 'add_employee.html', {'error_message_emp_id': error_message_emp_id, 'dep_select_name':dep_select_name})

            if emp.objects.filter(emp_id=emp_id).exists():
                error_message_emp_exist = 'This Employee ID is already in use.'
                return render(request, 'add_employee.html', {'error_message_emp_exist':error_message_emp_exist, 'dep_select_name':dep_select_name})
            # Validate mobile_number
            mobile_number_validator = RegexValidator(
                regex=r'^[6-9]\d{9}$',
                message='Enter a valid 10-digit mobile number starting with 6, 7, 8, or 9.',
            )
            mobile_number_validator(mobile_number)

            # Validate email
            email_field = emp._meta.get_field('email')
            if email_field.validators:
                validate_email = email_field.validators[0]
                validate_email(email)
            else:
                # Handle the case where there are no validators for the 'email' field
                error_messages.append('No validators found for the email field.')
                return render(request, 'add_employee.html', {'error_messages': error_messages})

            dob_date = datetime.strptime(dob, '%Y-%m-%d').date()

            # Check if dob is greater than or equal to the year 2010
            if dob_date.year >= 2010:
                error_message_dob='Date of birth must be before the year 2010.'
                return render(request, 'add_employee.html', {'error_message_dob': error_message_dob})

            if User.objects.filter(username=username).exists():
                error_message_username = 'This username is already in use. Try a different one.'
                return render(request, 'add_employee.html', {'error_message_username':error_message_username})
            # Perform password validation
            if not (len(password) >= 8 and any(c.isupper() for c in password) and any(c.isdigit() for c in password) and any(c in "!@#$%^&*" for c in password)):
                error_message_password = "Password must contain at least 8 characters. At least one uppercase character.At least one special character,and at least one number."
                return render(request, 'add_employee.html', {'error_message_password':error_message_password})

            if password != confirm_password:
                error_message_confirm = "Password and confirm password do not match."
                return render(request, 'add_employee.html', {'error_message_confirm':error_message_confirm})
            user = User.objects.create_user(username=username, password=password, email=email)
            # Assign the user to the "manager" group
            user.groups.add(employee_group)
            # Create employee instance with dep_name
            new_employee = emp(
                emp_id=emp_id,
                first_name=first_name.title(),
                last_name=last_name.title(),
                email=email,
                gender=gender,
                dob=dob,
                dep=dep_name,  # Assign dep_name here
                address=address,
                city=city,
                country=country,
                mobile_number=mobile_number,
                username=username
            )

            new_employee.full_clean()
            new_employee.save()

            success_message = 'Employee added successfully!'
            return render(request, 'add_employee.html', {'success_message': success_message, 'dep_select_name':dep_select_name})

        except ValueError:
            error_messages.append('Invalid date format for Date of Birth.')
            return render(request, 'add_employee.html', {'error_messages': error_messages, 'dep_select_name':dep_select_name})
        except ValidationError as e:
            error_messages = e.messages

        except OperationalError as oe:
            error_messages = 'Database connection error. Please check your database server: ' + str(oe)

        except IntegrityError as e:
            if 'unique constraint' in str(e):
                error_messages = 'An employee with the same ID already exists.'
            else:
                error_messages = 'An integrity error occurred while adding the employee. Please try again later.'


    return render(request, 'add_employee.html', {'error_messages': error_messages, 'dep_select_name': dep_select_name})





def manage_emp(request):
    try:
        data=emp.objects.all()
        return render(request, 'manage_emp.html', {'data':data })
    except OperationalError as O:
        error_message = 'Database connection error. Please check your database server.'
        return render(request, 'manage_emp.html', {'error_message': error_message})
    return render(request, 'manage_emp.html')



def update_emp(request, id):
    success_message = ""
    error_messages = ""

    # Assume dep_name is None by default
    dep_name = None

    existing_emp = get_object_or_404(emp, id=id)
    try:
        data = emp.objects.get(id=id)
    except emp.DoesNotExist:
        return HttpResponse("Employee not found ")
    dep_select_name = department.objects.all()

    if request.method == 'POST':
        emp_id = request.POST['emp_id']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        gender = request.POST['gender']
        dob = request.POST['dob']

        # Check if 'dep' key exists in the POST data
        dep_name = request.POST['dep']

        address = request.POST['address']
        city = request.POST['city']
        country = request.POST['country']
        mobile_number = request.POST['mobile_number']

        try:
            # Check if the updated department name already exists
            if emp_id != existing_emp.emp_id and emp.objects.filter(emp_id=emp_id).exists():
                error_message_emp_exist = 'This Employee ID is already in use.'
                return render(request, 'update_emp.html', {'existing_emp': existing_emp, 'dep_select_name': dep_select_name, 'error_message_emp_exist': error_message_emp_exist, 'data': data,})

            pattern = re.compile(r'^([a-zA-Z]{2,5}\d{3,5})$')

            if not pattern.match(emp_id):
                error_message_emp_id = 'Employee ID must be in the alph(2-5)+numeric(3-5) format'
                return render(request, 'update_emp.html', {'existing_emp': existing_emp, 'dep_select_name': dep_select_name, 'error_message_emp_id': error_message_emp_id, 'data': data,})

            # Validate mobile_number
            mobile_number_validator = RegexValidator(
                regex=r'^[6-9]\d{9}$',
                message='Enter a valid 10-digit mobile number starting with 6, 7, 8, or 9.',
            )
            mobile_number_validator(mobile_number)

            # Validate email
            email_field = emp._meta.get_field('email')
            if email_field.validators:
                validate_email = email_field.validators[0]
                validate_email(email)
            else:
                # Handle the case where there are no validators for the 'email' field
                error_messages.append('No validators found for the email field.')
                return render(request, 'update_emp.html', {'existing_emp': existing_emp, 'dep_select_name': dep_select_name, 'error_messages': error_messages, 'data': data,})

            if dob:
                try:
                    dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
                    # Check if dob is greater than or equal to the year 2010
                    if dob_date.year >= 2010:
                        error_message_dob = 'Date of birth must be before the year 2010.'
                        return render(request, 'update_emp.html', {'existing_emp': existing_emp, 'dep_select_name': dep_select_name, 'error_message_dob': error_message_dob, 'data': data,})
                    existing_emp.dob = dob_date  # Convert the string to datetime.date
                except ValueError:
                    error_messages.append('Invalid date format for Date of Birth.')
                    return render(request, 'update_emp.html', {'existing_emp': existing_emp, 'dep_select_name': dep_select_name, 'error_messages': error_messages, 'data': data,})
            else:
                existing_emp.dob = None  # Handle the case where 'dob' is empty, if necessary

            existing_emp.emp_id = emp_id
            existing_emp.first_name = first_name
            existing_emp.last_name = last_name
            existing_emp.email = email
            existing_emp.gender = gender
            existing_emp.dep = dep_name  # Assign dep_name here
            existing_emp.address = address
            existing_emp.city = city
            existing_emp.country = country
            existing_emp.mobile_number = mobile_number

            existing_emp.save()

            success_message = 'Employee Updated successfully!'
            return render(request, 'update_emp.html', {'existing_emp': existing_emp, 'dep_select_name': dep_select_name, 'success_message': success_message, 'data': data,})

        except ValidationError as e:
            error_messages = e.messages

        except OperationalError as oe:
            error_messages = 'Database connection error. Please check your database server: ' + str(oe)

        except IntegrityError as e:
            if 'unique constraint' in str(e):
                error_messages = 'An employee with the same ID already exists.'
            else:
                error_messages = 'An integrity error occurred while adding the employee. Please try again later.'


    return render(request, 'update_emp.html', {'data': data, 'existing_emp': existing_emp, 'dep_select_name': dep_select_name, 'error_messages': error_messages})



def delete_emp(request, id):
    try:
        employee = emp.objects.get(id=id)
        user = User.objects.get(username=employee.username)
    except (emp.DoesNotExist, User.DoesNotExist):
        return HttpResponse("Employee or User not found")

    # Delete the associated user first
    user.delete()

    # Now delete the employee record
    employee.delete()

    return redirect('manage_emp')




def emp_login(request):
    # Handle user login
    error_messages=""
    success_message=""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:

            #CsrfViewMiddleware().process_view(request, None, (), {})
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Check if the user belongs to the "manager" group
                if user.groups.filter(name='employee').exists():
                    login(request, user)
                    # User is a manager
                    # Do something for managers
                    request.session['username']=username
                    # Set a success message
                    success_message="Login successful. Welcome to the Employee dashboard!"


                    # Replace 'manager_dashboard' with the actual URL for the manager's dashboard

                else:
                    # User is not in the "manager" group
                    error_message = 'This username or password is incorrect.'
                    # Handle as needed, you can redirect to the login page or render the login form with an error message
                    return render(request, 'emp_login.html', {'error_message': error_message})

            else:
                error_message = 'This username or password is incorrect.'
                # Handle as needed, you can redirect to the login page or render the login form with an error message
                return render(request, 'emp_login.html', {'error_message': error_message})

        except IntegrityError as e:
            # IntegrityError occurred
            error_messages = 'An integrity error occurred while authenticating. Please try again later.'
        except OperationalError as e:
            # OperationalError occurred
            error_messages = 'A database connection error occurred. Please check your database server.'

    # Render login form for GET request
    return render(request, 'emp_login.html',{'error_messages':error_messages, 'success_message':success_message})



def emp_dashboard(request):
    username = request.user.username
    emp_instance = None

    if username:
        try:
            # Retrieve all groups of the current user
            user_groups = request.user.groups.all()

            # Check if there is a group with the same name as the username
            emp_instance = next((group for group in user_groups if group.name == username), None)

        except User.DoesNotExist:
            # Handle the case where the user does not exist
            pass

    return render(request, 'emp_dashboard.html', {'emp_instance': emp_instance})



def emplogout(request):
    logout(request)
    return redirect('home')



@login_required
def emp_change_creds(request):
    error_messages = ""
    success_message = ""
    error_message_p = ""
    error_message_u = ""

    # Assuming that the logged-in user is in the "manager" group
    user = request.user

    if request.method == 'POST':
        try:
            old_password = request.POST['old_password']
            new_password = request.POST['new_password']
            confirm_new_password = request.POST['confirm_new_password']
            new_username = request.POST['new_username']

            # Validate old password
            if not user.check_password(old_password):
                error_message_p = "Old password is incorrect."
            elif new_password != confirm_new_password:
                error_message_p = "New password and confirm password do not match."
            elif not (len(new_password) >= 8 and any(c.isupper() for c in new_password) and any(c.isdigit() for c in new_password) and any(c in "!@#$%^&*" for c in new_password)):
                error_message_p = "New password must contain at least 8 characters, one uppercase character, one digit, and one special character."
            elif new_username != user.username and User.objects.filter(username=new_username).exists():
                error_message_u = 'This username is already in use. Try a different one.'
            else:
                # Update the username and password
                user.username = new_username
                user.set_password(new_password)
                user.save()

                # Update the corresponding emp instance's username
                emp_instance = emp.objects.get(email=user.email)
                emp_instance.username = new_username
                emp_instance.save()


                # Update the leaves entry if it exists
                leave_instances = leaves.objects.filter(email=user.email)
                for leave_instance in leave_instances:
                    leave_instance.username = new_username
                    leave_instance.save()


                # Log out the user
                logout(request)
                success_message = "Password and username updated successfully. Please log in again."
                # Redirect to the login page
                return redirect('emp_login')

        except OperationalError as oe:
            error_messages = 'Database connection error. Please check your database server: {}'.format(oe)

        except IntegrityError as e:
            # IntegrityError occurred
            error_messages = 'An integrity error occurred while authenticating. Please try again later.'

    return render(request, 'emp_change_creds.html', {
        'error_messages': error_messages,
        'error_message_p': error_message_p,
        'error_message_u': error_message_u,
    })



def appy_leave(request):
    error_messages = ""
    success_message =""
    user = request.user
    email = user.email
    username = user.username
    username_from_session = request.session.get('username', '')

    leave_type_list = leavetypes.objects.all()

    if request.method == 'POST':
        try:

            email = request.POST['email']
            leave_type = request.POST['leave_type']
            from_date_str = request.POST['from_date']
            to_date_str = request.POST['to_date']
            description = request.POST['description']

            # Convert string dates to datetime.date objects
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()


            today = date.today()
            if from_date < today:
                error_message1 = "From Date cannot be before today."
                return render(request, 'appy_leave.html', {'username':username, 'error_message1': error_message1, 'leave_type_list': leave_type_list})

            if to_date < from_date:
                error_message2 = "To Date must be after From Date."
                return render(request, 'appy_leave.html', {'username':username, 'error_message2': error_message2, 'leave_type_list': leave_type_list})

            leave_instance = leaves(
                username=username,
                email=email,
                leave_type=leave_type,
                from_date=from_date,
                to_date=to_date,
                description=description,
            )
            leave_instance.save()

            # Save username in the session
            request.session['username'] = username

            success_message = 'Successfully applied leave.'
            return render(request, 'appy_leave.html', {'username':username, 'success_message': success_message,'leave_type_list': leave_type_list})

        except OperationalError as oe:
            error_messages = 'Database connection error. Please check your database server: {}'.format(oe)

        except IntegrityError as e:
            # IntegrityError occurred
            error_messages = 'An integrity error occurred while authenticating. Please try again later.'

    # Retrieve the username from the session
    username_from_session = request.session.get('username', '')

    leave_type_list = leavetypes.objects.all()
    value_today = date.today().strftime("%d-%m-%Y")
    return render(request, 'appy_leave.html', {'value_today': value_today,
    'error_messages': error_messages,
    'username':username,
    'success_message':success_message,
    'leave_type_list': leave_type_list,
    'username_from_session': username_from_session})


def leave_status(request):
    error_messages = ""

    try:
        # Retrieve username from the session
        username = request.user.username

        if username:
            try:
                # Assuming ForeignKey relationship between 'leaves' and 'emp' through 'username'
                leave_applications = leaves.objects.filter(username=username)
            except leaves.DoesNotExist:
                leave_applications = None

            try:
                # Retrieve the employee instance based on username
                emp_instance = emp.objects.get(username=username)
            except emp.DoesNotExist:
                emp_instance = None

            if leave_applications is not None and emp_instance is not None:
                return render(request, 'leave_status.html', {'leave_applications': leave_applications, 'emp_instance': emp_instance})
            else:
                # Handle the case where no leave applications are found or emp_instance is not available
                return render(request, 'error.html', {'message': 'No leave applications found or employee instance not found'})
        else:
            # Handle the case where username is not available in the session
            return render(request, 'error.html', {'message': 'Username not found in session'})

    except OperationalError as oe:
        error_messages = 'Database connection error. Please check your database server: {}'.format(oe)

    except IntegrityError as e:
        # IntegrityError occurred
        error_messages = 'An integrity error occurred while authenticating. Please try again later.'

    return render(request, 'leave_status.html', {'error_messages': error_messages})

def error(request):
    message = "An error occurred. Please try again later."  # Customize the error message as needed
    return render(request, 'error.html', {'message': message})


def admin_leaves(request):
    error_messages=""

    try:
        # Filter the leaves queryset to include only records with Status 'pending'
        data = leaves.objects.filter(Status='pending')
    except OperationalError as oe:
        error_messages = 'Database connection error. Please check your database server: {}'.format(oe)

    except IntegrityError as e:
        # IntegrityError occurred
        error_messages = 'An integrity error occurred while authenticating. Please try again later.'

    return render(request, 'admin_leaves.html', {'data': data, 'error_messages':error_messages})


def accept_leave(request, id):
    # Your logic to accept a leave
    # Example: Change the status of the leave to 'accepted'
    leave = leaves.objects.get(pk=id)
    leave.Status = 'accepted'
    leave.save()
    return redirect('admin_leaves')


def reject_leave(request, id):
    # Your logic to reject a leave
    # Example: Change the status of the leave to 'rejected'
    leave = leaves.objects.get(pk=id)
    leave.Status = 'rejected'
    leave.save()
    return redirect('admin_leaves')  # Redirect to the admin leaves page
