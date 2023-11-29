from django.db import models

# Create your models here.
from django.db import models
from datetime import date
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re





class admindata(models.Model):

    admin_id_validator = RegexValidator(
        regex=r'^([a-z]{0,5}[A-Z]{0,5}\d{3,5})$',
        message='Admin ID must be a combination of 3 uppercase characters followed by 3 to 5 numbers.',
    )


    admin_id = models.CharField(max_length=10,  unique=True, validators=[admin_id_validator])
    first_name= models.CharField(max_length=100)
    last_name= models.CharField(max_length=100)
    email=models.EmailField()

    mobile_number_validator = RegexValidator(
        regex=r'^[6-9]\d{9}$',
        message='Enter a valid 10-digit mobile number starting with 6, 7, 8, or 9.',
    )

    mobile_number = models.CharField(max_length=10, validators=[mobile_number_validator])


    reg_date = models.DateField(default=date.today)
    username= models.CharField(max_length=100, default='username')
    is_admin = models.CharField(max_length=3, default='yes', editable=False)

    def __str__(self):
        return str(self.id)

class department(models.Model):

    dep_name=models.CharField(max_length=100, unique=True)
    dep_short_name=models.CharField(max_length=5)

    alphanumeric_validator = RegexValidator(
        regex=r'^([A-Z]{0,5}\d{0,5})*$',
        message='Only alphanumeric characters are allowed.',
    )

    dep_code=models.CharField(max_length=10,  validators=[alphanumeric_validator])
    reg_date = models.DateField(default=date.today)

    def __str(self):
        return self.dep_name

class emp(models.Model):
    alphanumeric_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9]*$',
        message='Only alphanumeric characters are allowed.',
    )
    emp_id=models.CharField(max_length=10,  unique=True, validators=[alphanumeric_validator])


    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    email=models.EmailField()

    gender = models.CharField(max_length=100)
    dob = models.DateField(null=False)

    dep=models.CharField(max_length=100)

    def clean(self):
        super().clean()
        current_year = date.today().year
        if self.dob and self.dob.year >= 2010:
            raise ValidationError({'dob': ['Date of birth must be before the year 2010.']})
    address = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=150, null=True)

    mobile_number_validator = RegexValidator(
        regex=r'^[6-9]\d{9}$',
        message='Enter a valid 10-digit mobile number starting with 6, 7, 8, or 9.',
    )

    mobile_number = models.CharField(max_length=10, validators=[mobile_number_validator])
    username = models.CharField(max_length=100, null=False, default= 'username')
    is_admin = models.CharField(max_length=3, default='no', editable=False)
    reg_date = models.DateField(default=date.today)

    def __str__(self):
        return str(self.id)

class leavetypes(models.Model):

    leave_name= models.CharField(max_length=100, unique=True)

    alphanumeric_validator = RegexValidator(
        regex=r'^([A-Z]{0,5}\d{0,5})*$',
        message='Only alphanumeric characters are allowed.',
    )

    leave_code=models.CharField(max_length=10, null=False, default='AAA000', validators=[alphanumeric_validator])
    description=models.TextField(null=True)
    reg_date = models.DateField(default=date.today)

    def __str__(self):
        return self.leave_name

class leaves(models.Model):

    username=models.CharField(max_length=100)
    leave_type=models.CharField(max_length=100)

    email=models.EmailField(default='@gmail.com')

    from_date = models.DateField(null=True)
    to_date=models.DateField(null=True)

    def clean(self):
        if self.from_date:
            today = date.today()
            if self.from_date < today:
                raise ValidationError("Invalid date selections", code='invalid')

        if self.from_date and self.to_date:
            if self.to_date < self.from_date:
                raise ValidationError("Invalid date selections", code='invalid')

    description=models.TextField(null=True)
    posting_date = models.DateField(default=date.today)

    Status = models.CharField(max_length=12,default='pending')


    class Meta:
        permissions = [
            ("can_change_leave_status", "Can change leave status"),
        ]


    def __str__(self):
        return f"Leave for {self.id}"
