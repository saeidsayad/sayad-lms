from django import forms
from django.contrib.auth.forms import UserCreationForm
from allauth.account.forms import SignupForm
from .models import CustomUser
from courses.models import Course

# فرم ۱: برای استفاده در پنل ادمین (بدون تغییر)
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'is_student')
        
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

# فرم ۲: فرم ثبت‌نام نهایی (ترکیب نام + انتخاب دوره)
class CustomSignupForm(SignupForm):
    # --- بخش ۱: فیلدهای جدید (نام و نام خانوادگی) ---
    first_name = forms.CharField(
        max_length=30,
        label='نام',
        widget=forms.TextInput(attrs={
            'placeholder': 'نام خود را وارد کنید',
            'class': 'form-control'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        label='نام خانوادگی',
        widget=forms.TextInput(attrs={
            'placeholder': 'نام خانوادگی را وارد کنید',
            'class': 'form-control'
        })
    )

    # --- بخش ۲: فیلد قبلی شما (انتخاب دوره) ---
    course = forms.ModelChoiceField(
        queryset=Course.objects.filter(is_active_for_signup=True), # فرض بر اینکه این فیلد را در مدل دارید
        label='انتخاب دوره آموزشی',
        empty_label="لطفا دوره خود را انتخاب کنید...",
        widget=forms.Select(attrs={'class': 'form-select'}) # کلاس مناسب برای لیست کشویی
    )

    def save(self, request):
        # ۱. ساخت یوزر اولیه با ایمیل و پسورد (توسط Allauth)
        user = super(CustomSignupForm, self).save(request)
        
        # ۲. ذخیره نام و نام خانوادگی در دیتابیس
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        # تنظیم پیش‌فرض دانشجو بودن
        user.is_student = True
        
        # ۳. ثبت نام دانشجو در دوره انتخابی (کد قبلی شما)
        course = self.cleaned_data['course']
        if course:
            course.students.add(user)
            
        user.save()
        return user

# فرم ۳: ویرایش پروفایل (بدون تغییر)
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
        }

