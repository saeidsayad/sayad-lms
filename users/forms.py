from django import forms
from django.contrib.auth.forms import UserCreationForm
from allauth.account.forms import SignupForm
from .models import CustomUser
from courses.models import Course


# فرم ۱: برای استفاده در پنل ادمین (زمانی که شما دستی کاربر می‌سازید)
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')
        
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

# فرم ۲: برای ثبت‌نام خود دانشجو در سایت (با قابلیت انتخاب دوره)
class CustomSignupForm(SignupForm):
    course = forms.ModelChoiceField(
        queryset=Course.objects.filter(is_active_for_signup=True),
        label='انتخاب دوره آموزشی',
        empty_label="لطفا دوره خود را انتخاب کنید...",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        course = self.cleaned_data['course']
        course.students.add(user)
        return user

# فرم ۳: ویرایش پروفایل کاربر
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
