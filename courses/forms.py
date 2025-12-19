from django import forms
from .models import Submission


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['submitted_file', 'description']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'توضیحات اختیاری...',
                'class': 'form-control' # کلاس بوت‌استرپ
            }),
            'submitted_file': forms.ClearableFileInput(attrs={
                'class': 'form-control' # کلاس بوت‌استرپ
            }),
        }
        labels = {
            'submitted_file': 'انتخاب فایل (ZIP یا PY)',
            'description': 'توضیحات'
        }