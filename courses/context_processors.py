from .models import SiteSetting

def website_settings(request):
    # اولین ردیف تنظیمات را می‌گیرد
    setting = SiteSetting.objects.first()
    return {'site_setting': setting}
