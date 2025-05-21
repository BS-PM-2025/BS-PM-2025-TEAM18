from django import forms
from .models import Request
from .models import Rating

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['title', 'description', 'request_type']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'נושא הבקשה'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'תיאור הבקשה'}),
            'request_type': forms.Select(attrs={'class': 'form-control'}),
        }

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
