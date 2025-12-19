from django.contrib import admin
from .models import CourseTemplate, ExerciseTemplate, Course, Exercise, Submission
from .models import EnrollmentRequest, SiteSetting 
from django.utils.html import format_html


# --- مدیریت الگوها ---
class ExerciseTemplateInline(admin.StackedInline):
    model = ExerciseTemplate
    extra = 1

@admin.register(CourseTemplate)
class CourseTemplateAdmin(admin.ModelAdmin):
    inlines = [ExerciseTemplateInline]

# --- اکشن‌های سفارشی برای تمرینات ---
@admin.action(description='🔓 باز کردن قفل تمرین‌های انتخاب شده')
def unlock_exercises(modeladmin, request, queryset):
    queryset.update(is_locked=False)

@admin.action(description='🔒 قفل کردن تمرین‌های انتخاب شده')
def lock_exercises(modeladmin, request, queryset):
    queryset.update(is_locked=True)

# --- مدیریت دوره‌های اجرایی ---
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'template', 'course_number', 'created_at']

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'is_locked']
    list_filter = ['course', 'is_locked'] # فیلتر سمت راست خیلی مهم است
    list_editable = ['is_locked'] # روش سریع برای باز کردن تکی
    actions = [unlock_exercises, lock_exercises] # اضافه کردن دکمه‌های گروهی بالا

from django.utils.html import format_html

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    # ستون‌هایی که در جدول نمایش داده می‌شوند
    list_display = ['student_info', 'course_info', 'exercise_info', 'file_link', 'submitted_at_formatted', 'score_status']
    
    # فیلترهای سمت راست (بسیار کاربردی)
    list_filter = ['exercise__course', 'exercise__is_locked', 'submitted_at']
    
    # باکس جستجو (روی ایمیل و نام دانشجو)
    search_fields = ['student__email', 'student__first_name', 'student__last_name', 'description']
    
    # --- توابع کمکی برای نمایش زیباتر ---

    def student_info(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name} ({obj.student.email})"
    student_info.short_description = 'دانشجو'

    def course_info(self, obj):
        return f"دوره {obj.exercise.course.course_number}"
    course_info.short_description = 'دوره'

    def exercise_info(self, obj):
        return f"تمرین {obj.exercise.order}: {obj.exercise.title}"
    exercise_info.short_description = 'تمرین'

    def file_link(self, obj):
        if obj.submitted_file:
            # ایجاد دکمه دانلود رنگی
            return format_html(
                '<a href="{}" class="button" style="background-color: #28a745; color: white; padding: 5px 10px; border-radius: 5px; text-decoration: none;" download>📥 دانلود فایل</a>',
                obj.submitted_file.url
            )
        return "ندارد"
    file_link.short_description = 'فایل ارسالی'

    def submitted_at_formatted(self, obj):
        # نمایش تاریخ به صورت تمیز
        return obj.submitted_at.strftime("%Y/%m/%d - %H:%M")
    submitted_at_formatted.short_description = 'تاریخ ارسال'

    def score_status(self, obj):
        if obj.score is None:
            return format_html('<span style="color: orange;">⏳ نمره داده نشده</span>')
        return format_html('<span style="color: blue; font-weight: bold;">{} / 100</span>', obj.score)
    score_status.short_description = 'وضعیت نمره'
    

# اکشن برای تایید درخواست‌ها
@admin.action(description='✅ تایید درخواست و عضویت دانشجو در دوره')
def approve_enrollment(modeladmin, request, queryset):
    for req in queryset:
        # 1. دانشجو را به دوره اضافه کن
        req.course.students.add(req.student)
        # 2. درخواست را پاک کن (چون دیگه انجام شد)
        req.delete()

@admin.register(EnrollmentRequest)
class EnrollmentRequestAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'created_at']
    list_filter = ['course']
    actions = [approve_enrollment]
    

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    # این تابع باعث می‌شود نتوانید بیشتر از یک تنظیمات بسازید (فقط یکی کافیست)
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return True
