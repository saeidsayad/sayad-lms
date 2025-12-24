from django.urls import path
from . import views
from .views import CustomSignupView


app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.edit_profile, name='edit_profile'),
    path("accounts/signup/", CustomSignupView.as_view(), name="account_signup"),
]
