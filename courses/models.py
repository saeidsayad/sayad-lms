from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import os


# --- بخش الگوها (Templates) ---
# این‌ها فقط برای کپی‌برداری هستند و دانشجو در این‌ها ثبت‌نام نمی‌کند
class CourseTemplate(models.Model):
    title = models.CharField(max_length=200, verbose_name='عنوان کلی دوره (مثلا پایتون مقدماتی)')
    description = models.TextField(verbose_name='توضیحات پیش‌فرض')
    
    def __str__(self):
        return self.title

class ExerciseTemplate(models.Model):
    course_template = models.ForeignKey(CourseTemplate, on_delete=models.CASCADE, related_name='exercise_templates')
    title = models.CharField(max_length=200, verbose_name='عنوان تمرین')
    problem_statement = models.TextField(verbose_name='صورت سوال')
    order = models.PositiveIntegerField(default=1, verbose_name='شماره ترتیب')

    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.title} (الگو)"

# --- بخش اجرایی (Active Courses) ---
# این‌ها دوره‌های واقعی هستند (مثل دوره 137)
class Course(models.Model):
    # هر دوره واقعی از یک الگو پیروی می‌کند
    template = models.ForeignKey(CourseTemplate, on_delete=models.PROTECT, verbose_name='نوع دوره')
    course_number = models.PositiveIntegerField(verbose_name='شماره دوره (مثلا 137)')
    
    # فیلد تایتل را نگه می‌داریم اما اتوماتیک پر می‌کنیم
    title = models.CharField(max_length=200, blank=True, verbose_name='نام کامل دوره')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='courses_joined', blank=True, verbose_name='دانشجویان')
    is_active_for_signup = models.BooleanField(default=True, verbose_name='قابل انتخاب در ثبت‌نام')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['template', 'course_number'] # نمیتوانیم دو تا پایتون دوره 137 داشته باشیم

    def save(self, *args, **kwargs):
        # ساخت اتوماتیک اسم دوره
        if not self.title:
            self.title = f"{self.template.title} - دوره {self.course_number}"
        if not self.description:
            self.description = self.template.description
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Exercise(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exercises')
    title = models.CharField(max_length=200)
    problem_statement = models.TextField()
    is_locked = models.BooleanField(default=True, verbose_name='قفل است؟')
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.course_number} - {self.title}"


def submission_file_path(instance, filename):
    # instance همان آبجکت Submission است که دارد ذخیره می‌شود
    
    # گرفتن نام کاربری (اگر یوزرنیم نداشت، بخش اول ایمیل)
    user_folder = instance.student.username or instance.student.email.split('@')[0]
    
    # نام پوشه دوره
    course_folder = f"Course_{instance.exercise.course.course_number}"
    
    # نام پوشه تمرین
    exercise_folder = f"Ex_{instance.exercise.order}"
    
    # مسیر نهایی: submissions / نام_دانشجو / شماره_دوره / شماره_تمرین / اسم_فایل
    return f'submissions/{user_folder}/{course_folder}/{exercise_folder}/{filename}'


class Submission(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submitted_file = models.FileField(
        upload_to=submission_file_path,
        verbose_name='فایل تمرین'
    )
    description = models.TextField(blank=True, null=True)
    score = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    teacher_comment = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    

class EnrollmentRequest(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollment_requests')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollment_requests')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ درخواست')

    class Meta:
        # جلوگیری از ارسال تکراری درخواست
        unique_together = ['student', 'course']
        verbose_name = 'درخواست ثبت‌نام'
        verbose_name_plural = 'درخواست‌های ثبت‌نام'

    def __str__(self):
        return f"{self.student} -> {self.course}"
