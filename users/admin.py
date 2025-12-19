from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # فیلدهایی که در لیست کاربران نمایش داده می‌شوند
    list_display = ['email', 'username', 'is_student', 'is_active', 'is_staff']
    
    # فیلد is_student را به فرم ویرایش کاربر اضافه می‌کنیم
    fieldsets = UserAdmin.fieldsets + (
        ('اطلاعات تکمیلی', {'fields': ('is_student',)}),
    )
    
    # فیلد is_student را به فرم افزودن کاربر هم اضافه می‌کنیم
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('اطلاعات تکمیلی', {'fields': ('is_student',)}),
    )
