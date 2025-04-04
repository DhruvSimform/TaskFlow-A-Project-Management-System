from django.contrib import admin

from .models import Department


# Register your models here.
class AdminDepartment(admin.ModelAdmin):
    list_display = [field.name for field in Department._meta.fields]


admin.site.register(Department, AdminDepartment)
