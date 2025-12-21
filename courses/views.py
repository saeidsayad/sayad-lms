from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Course, Exercise, Submission
from .forms import SubmissionForm
from .models import Course, EnrollmentRequest
from django.core.mail import send_mail
from django.conf import settings


@login_required
def course_list(request):
    # دوره‌های فعلی دانشجو
    my_courses = request.user.courses_joined.all().order_by('-created_at')

    # دوره‌های قابل ثبت‌نام (آن‌هایی که دانشجو ندارد)
    available_courses = Course.objects.filter(is_active_for_signup=True).exclude(students=request.user).order_by('-created_at')

    # لیست آی‌دی دوره‌هایی که دانشجو براشون درخواست داده و هنوز تایید نشده
    pending_ids = EnrollmentRequest.objects.filter(student=request.user).values_list('course_id', flat=True)

    context = {
        'my_courses': my_courses,
        'available_courses': available_courses,
        'pending_ids': pending_ids,
    }
    return render(request, 'courses/course_list.html', context)

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    
    # چک می‌کنیم آیا دانشجو در این دوره ثبت نام کرده است یا نه
    is_enrolled = request.user in course.students.all()
    
    exercises = []
    # مقادیر اولیه برای درصد پیشرفت (برای حالتی که ثبت‌نام نکرده)
    progress_percentage = 0
    submitted_count = 0
    total_exercises = 0

    if is_enrolled:
        # فقط تمرینات همین دوره را می‌گیریم
        exercises = course.exercises.all().order_by('order')
        
        # 1. محاسبه تعداد کل تمرین‌های این دوره
        total_exercises = exercises.count()

        # 2. محاسبه تعداد تمرین‌هایی که دانشجو انجام داده
        # نکته: از values و distinct استفاده می‌کنیم تا اگر برای یک تمرین چند بار فایل فرستاده، فقط یکی حساب شود
        submitted_count = Submission.objects.filter(
            student=request.user,
            exercise__in=exercises
        ).values('exercise').distinct().count()

        # 3. محاسبه درصد (با شرط اینکه مخرج صفر نشود)
        if total_exercises > 0:
            progress_percentage = int((submitted_count / total_exercises) * 100)

    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'exercises': exercises,
        
        # ارسال متغیرهای جدید به قالب
        'progress_percentage': progress_percentage,
        'submitted_count': submitted_count,
        'total_exercises': total_exercises,
    }
    return render(request, 'courses/course_detail.html', context)

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    
    # چک می‌کنیم اگر قبلا عضو است
    if request.user in course.students.all():
        messages.warning(request, 'شما قبلاً در این دوره عضو شده‌اید.')
    # چک می‌کنیم اگر قبلا درخواست داده
    elif EnrollmentRequest.objects.filter(student=request.user, course=course).exists():
        messages.info(request, 'درخواست شما قبلاً ارسال شده و در انتظار تایید است.')
    else:
        # ایجاد درخواست جدید (به جای اضافه کردن مستقیم)
        EnrollmentRequest.objects.create(student=request.user, course=course)
        messages.success(request, f'درخواست ثبت‌نام در دوره "{course.title}" برای استاد ارسال شد. لطفاً منتظر تایید بمانید.')
    
    return redirect('courses:course_list')

@login_required
def exercise_detail(request, exercise_id):
    exercise = get_object_or_404(Exercise, pk=exercise_id)
    
    if exercise.is_locked:
        return HttpResponseForbidden("این تمرین قفل است.")

    if request.user not in exercise.course.students.all():
        messages.error(request, "شما در این دوره ثبت نام نکرده‌اید.")
        return redirect('courses:course_detail', course_id=exercise.course.id)

    if request.method == 'POST':
        # نکته کلیدی: request.FILES برای دریافت فایل ضروری است
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = request.user
            submission.exercise = exercise
            submission.save()
            messages.success(request, 'فایل شما با موفقیت آپلود شد.')
            return redirect('courses:exercise_detail', exercise_id=exercise.id)
    else:
        form = SubmissionForm()

    previous_submissions = exercise.submissions.filter(student=request.user).order_by('-submitted_at')

    context = {
        'exercise': exercise,
        'form': form,
        'previous_submissions': previous_submissions
    }
    return render(request, 'courses/exercise_detail.html', context)

def home_page(request):
    # اگر کاربر لاگین کرده، بفرستش به داشبورد دوره‌ها
    if request.user.is_authenticated:
        return redirect('courses:course_list')
    
    # اگر مهمان است، صفحه اصلی زیبا را نشان بده
    return render(request, 'home.html')

def contact_us(request):
    if request.method == 'POST':
        # 1. دریافت اطلاعات از فرم
        name = request.POST.get('name')
        user_email = request.POST.get('email') # ایمیل کاربر بازدیدکننده
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')

        # 2. ساختن متن ایمیلی که قراره برای شما بیاد
        # چون نمی‌تونیم ایمیل فرستنده رو ایمیل کاربر بذاریم (جیمیل بلاک میکنه)
        # مشخصات کاربر رو می‌نویسیم توی متن ایمیل
        full_message = f"""
        سلام مدیر، یک پیام جدید از سایت داری:

        👤 نام فرستنده: {name}
        ✉️ ایمیل فرستنده: {user_email}
        ----------------------------------
        📝 متن پیام:
        {message_text}
        """

        try:
            # 3. ارسال ایمیل
            send_mail(
                subject=f"📩 پیام تماس با ما: {subject}",  # عنوان ایمیل
                message=full_message,                     # متن ایمیل
                from_email=settings.DEFAULT_FROM_EMAIL,   # فرستنده (باید ایمیل خود سرور باشه)
                recipient_list=['test@gmail.com'],        # ⚠️ مقصدی که پیام‌ها بهش میرسه (ایمیل شما)
                fail_silently=False,
            )
            
            messages.success(request, 'پیام شما با موفقیت دریافت شد. به زودی با شما تماس می‌گیریم.')
        
        except Exception as e:
            # اگر خطایی خورد (مثلا قطعی اینترنت سرور)
            print(e) # چاپ خطا در لاگ برای دیباگ
            messages.error(request, 'متاسفانه خطایی در ارسال پیام رخ داد. لطفا بعدا تلاش کنید.')

        return redirect('contact')
        
    return render(request, 'contact.html')
