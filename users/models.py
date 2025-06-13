from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('lecturer', 'Lecturer'),
        ('secretary', 'Secretary'),
    ]
    LANGUAGE_CHOICES = [
        ('he', _('Hebrew')),
        ('en', _('English')),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_blocked = models.BooleanField(default=False)  # ✅ שדה חדש לחסימה
    preferred_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='he')  # ✅ שדה חדש לשפה

    def __str__(self):
        return f"{self.username} ({self.role})"


class Request(models.Model):
    REQUEST_TYPES = [
        ('extension', 'הארכת מועד'),
        ('appeal', 'ערעור ציון'),
        ('medical', 'אישור רפואי'),
    ]

    STATUS_CHOICES = [
        ('submitted', 'נשלחה'),
        ('in_progress', 'בטיפול'),
        ('approved', 'אושרה'),
        ('rejected', 'נדחתה'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    course = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    reason = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ שדה חדש לסיפור 29 – תאריך יעד
    due_date = models.DateField(null=True, blank=True)

    # ✅ שדה חדש לסיפור 36 – הערת המרצה בעת אישור/דחייה
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.username} - {self.get_request_type_display()}"


# ✅ טבלה חדשה לשמירת התראות
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.message}"


class Rating(models.Model):
    rating = models.IntegerField()  # ציון 1–5
    comment = models.TextField(blank=True, null=True)  # הערה (אופציונלי)
    created_at = models.DateTimeField(auto_now_add=True)  # תאריך שליחה

    def __str__(self):
        return f"דירוג: {self.rating} כוכבים"


class BugReport(models.Model):
    STATUS_CHOICES = [
        ('חדש', 'חדש'),
        ('טופל', 'טופל'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ שימוש נכון
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='חדש')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Request, Notification
from django.contrib.auth.models import User

@login_required
def remind_grade_appeals(request):
    appeals = Request.objects.filter(type='ערעור ציון', status='submitted')
    lecturers = User.objects.filter(profile__role='Lecturer')  # ודא שהשדה נכון

    for lecturer in lecturers:
        Notification.objects.create(
            to_user=lecturer,
            message=f'יש {appeals.count()} בקשות ערעור שממתינות לאישור.',
        )

    return redirect('secretary_dashboard')
