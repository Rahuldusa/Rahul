from django.contrib import admin

from .models import admindata, department, emp, leavetypes, leaves



admin.site.register(admindata)
admin.site.register(department)
admin.site.register(emp)
admin.site.register(leavetypes)
admin.site.register(leaves)
