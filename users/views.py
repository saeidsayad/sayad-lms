from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from allauth.account.views import SignupView
from smtplib import SMTPRecipientsRefused


# ویوی ثبت‌نام
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # مهم: کاربر را غیرفعال ذخیره می‌کنیم تا استاد تایید کند
            user.save()
            messages.success(request, 'ثبت‌نام با موفقیت انجام شد. لطفا منتظر تایید استاد باشید.')
            return redirect('users:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

# ویوی ورود (Login)
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # لاگین کردن کاربر
            user = form.get_user()
            login(request, user)
            # اگر پارامتری به نام next در url بود به آنجا برو، وگرنه برو به صفحه اصلی
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            return redirect('courses:course_list') # بعدا این مسیر را می‌سازیم
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# ویوی خروج (Logout)
def logout_view(request):
    logout(request)
    messages.info(request, 'شما با موفقیت خارج شدید.')
    return redirect('users:login')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # فرم را با اطلاعات ارسال شده پر می‌کنیم
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'اطلاعات پروفایل شما با موفقیت بروزرسانی شد.')
            return redirect('users:edit_profile')
    else:
        # فرم را با اطلاعات فعلی کاربر پر می‌کنیم تا ببیند
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/profile_edit.html', {'form': form})

class CustomSignupView(SignupView):
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(
                self.request,
                "ایمیل تأیید برای شما ارسال شد. لطفاً صندوق ورودی را بررسی کنید."
            )
            return response

        except SMTPRecipientsRefused:
            if self.user:
                self.user.delete()

            messages.error(
                self.request,
                "ایمیلی که وارد کرده‌اید معتبر نیست."
            )
            return self.form_invalid(form)
