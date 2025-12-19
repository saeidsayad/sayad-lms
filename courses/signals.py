from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Course, Exercise, ExerciseTemplate


@receiver(post_save, sender=Course)
def create_exercises_from_template(sender, instance, created, **kwargs):
    """
    وقتی یک دوره جدید ساخته می‌شود، تمرینات را از الگو کپی می‌کند
    """
    if created: # فقط بار اول که ساخته شد
        templates = ExerciseTemplate.objects.filter(course_template=instance.template)
        
        exercises_to_create = []
        for temp in templates:
            exercises_to_create.append(Exercise(
                course=instance,
                title=temp.title,
                problem_statement=temp.problem_statement,
                order=temp.order,
                is_locked=True # پیش‌فرض همه قفل هستند
            ))
        
        # ثبت یکجای همه تمرینات در دیتابیس (برای سرعت بالا)
        Exercise.objects.bulk_create(exercises_to_create)
