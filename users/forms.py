from django import forms
from .models import Request
from .models import Rating


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['request_type', 'course', 'subject', 'reason', 'attachment']

    # אם תרצי אפשר להגדיר גם וידג'טים לשדות, למשל:
    widgets = {
        'request_type': forms.Select(attrs={'class': 'form-control'}),
        'course': forms.Select(attrs={'class': 'form-control'}),
        'subject': forms.TextInput(attrs={'class': 'form-control'}),
        'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
    }

    # אם שדה קובץ רצוי לוודא שהוא לא חובה, או להוסיף ולידציה נוספת:
    attachment = forms.FileField(required=False)
# forms.py

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'comment']

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 1 or rating > 5:
            raise forms.ValidationError('הדירוג חייב להיות בין 1 ל־5.')
        return rating

from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()

class LecturerProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'feedback-input'}),
            'last_name': forms.TextInput(attrs={'class': 'feedback-input'}),
            'email': forms.EmailInput(attrs={'class': 'feedback-input'}),
        }
