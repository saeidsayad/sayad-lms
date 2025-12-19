from django.urls import path
from . import views


app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'), # لیست همه دوره‌ها
    path('<int:course_id>/', views.course_detail, name='course_detail'), # جزئیات یک دوره خاص
    path('<int:course_id>/enroll/', views.enroll_course, name='enroll'), # لینک ثبت‌نام در دوره
    path('exercise/<int:exercise_id>/', views.exercise_detail, name='exercise_detail'),
]
