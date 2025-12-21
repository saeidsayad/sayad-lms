from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser
from courses.models import Submission
from .forms import CustomUserCreationForm


# 1. تنظیمات نمایش تمرین‌ها
class SubmissionInline(admin.TabularInline):
    model = Submission
    fields = ['course_info', 'exercise_info', 'submitted_at_formatted', 'file_link', 'score', 'feedback']
    readonly_fields = ['course_info', 'exercise_info', 'submitted_at_formatted', 'file_link']
    extra = 0
    can_delete = False
    
    def course_info(self, obj):
        return obj.exercise.course.title
    course_info.short_description = "دوره"

    def exercise_info(self, obj):
        return f"تمرین {obj.exercise.order}: {obj.exercise.title}"
    exercise_info.short_description = "تمرین"

    def submitted_at_formatted(self, obj):
        return obj.submitted_at.strftime("%Y/%m/%d - %H:%M")
    submitted_at_formatted.short_description = "تاریخ ارسال"

    def file_link(self, obj):
        if obj.submitted_file:
            return format_html(
                '<a href="{}" style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 5px; text-decoration: none;" download>📥 دانلود</a>',
                obj.submitted_file.url
            )
        return "ندارد"
    file_link.short_description = "فایل"


# 2. تنظیمات اصلی ادمین
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    
    inlines = [SubmissionInline]
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_student', 'is_staff']
    ordering = ['email']

    # --- اصلاحیه مهم: حذف فیلدهای bio و profile_picture ---
    
    # تنظیمات صفحه ویرایش (Edit)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name')}), # فقط نام و نام خانوادگی
        ('وضعیت تحصیلی', {'fields': ('is_student',)}), # فیلد اختصاصی شما
        ('دسترسی‌ها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخ‌ها', {'fields': ('last_login', 'date_joined')}),
    )
    
    # تنظیمات صفحه افزودن (Add)
    
    add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': (
            'email',
            'first_name',
            'last_name',
            'is_student',
            'password1',
            'password2',
        ),
    }),
)

