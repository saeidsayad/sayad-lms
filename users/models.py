from django.db import models
from django.contrib.auth.models import AbstractUser
import random


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='آدرس ایمیل')
    is_student = models.BooleanField(default=True, verbose_name='دانشجو')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name'] 
    # توجه: username را در لیست بالا نگه دارید تا اگر خواستید با دستور createsuperuser ادمین بسازید به مشکل نخورید

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # بررسی می‌کنیم که آیا یوزرنیم تنظیم شده است یا خیر
        if not self.username:
            # قدم ۱: ساخت یک یوزرنیم اولیه از ترکیب نام و نام خانوادگی
            # فاصله‌ها را حذف می‌کنیم تا یوزرنیم یک‌تکه باشد
            base_username = f"{self.first_name}{self.last_name}".replace(" ", "")
            
            # اگر کاربر نام و نام خانوادگی وارد نکرده بود، از قسمت اول ایمیل استفاده کن
            if not base_username:
                base_username = self.email.split('@')[0]
            
            # قدم ۲: اطمینان از یکتا بودن (Uniqueness)
            candidate = base_username
            counter = 1
            
            # تا زمانی که کاربری با این یوزرنیم در دیتابیس وجود دارد، یک عدد رندوم به تهش اضافه کن
            while CustomUser.objects.filter(username=candidate).exists():
                # یک عدد تصادفی بین 10 تا 9999 به انتهای اسم اضافه می‌کند
                candidate = f"{base_username}{random.randint(10, 9999)}"
            
            # قدم ۳: تنظیم یوزرنیم نهایی
            self.username = candidate
            
        super().save(*args, **kwargs)
