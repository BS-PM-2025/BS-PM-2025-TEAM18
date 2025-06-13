from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .models import CustomUser, Request, Notification, Rating  # ✅ הוספתי גם Rating
from .forms import RequestForm, RatingForm
from .knowledge_base import knowledge_base  # ✅ ייבוא של מאגר השאלות-תשובות
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Rating  # לייבא את מודל הדירוגים
from django.db.models import Avg  # כדי לחשב ממוצע
from django.contrib import messages
from .models import BugReport
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.conf import settings
from datetime import date



# ------------------ פונקציות קיימות ------------------ #

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'שם המשתמש הזה כבר רשום במערכת.')
        else:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='student'
            )
            user.save()
            messages.success(request, 'נרשמת בהצלחה! ניתן כעת להתחבר למערכת.')
            return redirect('login')

    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_blocked:
                messages.error(request, 'החשבון שלך חסום. אנא פנה למנהל המערכת.')
                return redirect('login')
            login(request, user)
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'student':
                return redirect('student_dashboard')
            elif user.role == 'lecturer':
                return redirect('lecturer_dashboard')
            elif user.role == 'secretary':
                return redirect('secretary_dashboard')
        else:
            messages.error(request, 'פרטי ההתחברות שגויים. נסה שוב.')
    return render(request, 'login.html')

@login_required
def user_logout(request):
    logout(request)
    return render(request, 'logout.html')

def home(request):
    return render(request, 'home.html')  # שים לב שהדף הזה צריך להיבנות גם

@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
def student_dashboard(request):
    return render(request, 'student_dashboard.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Notification

@login_required
def lecturer_dashboard(request):
    if request.user.role != 'lecturer':
        return redirect('not_authorized')

    # שליפת ההתראות של המרצה הנוכחי
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()

    return render(request, 'lecturer_dashboard.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Notification

@require_POST
@login_required
def mark_notifications_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})



@login_required
def secretary_dashboard(request):
    # כל ההתראות שלא נקראו
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')

    # מספר ההתרעות שלא נקראו
    unread_count = unread_notifications.count()

    # אפשרות להוסיף פילטר נוסף לפי תאריך יעד (3 ימים אחרונים לדוגמה):
    recent_notifications = Notification.objects.filter(
        user=request.user,
        created_at__gte=timezone.now() - timedelta(days=3)
    ).order_by('-created_at')

    return render(request, 'secretary_dashboard.html', {
        'notifications': unread_notifications,
        'notifications_recent': recent_notifications,
        'unread_count': unread_count,
    })


@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('secretary_dashboard')



@login_required
def user_list(request):
    if request.user.role != 'admin':
        return render(request, 'not_authorized.html')
    users = CustomUser.objects.all()
    return render(request, 'user_list.html', {'users': users})

@login_required
def profile_view(request):
    return render(request, 'profile.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        if not request.user.check_password(current_password):
            messages.error(request, 'הסיסמה הנוכחית שהזנת אינה נכונה.')
        elif new_password != confirm_password:
            messages.error(request, 'הסיסמה החדשה לא תואמת את שדה האימות.')
        elif new_password == current_password:
            messages.error(request, 'הסיסמה החדשה חייבת להיות שונה מהסיסמה הנוכחית.')
        elif len(new_password) < 6:
            messages.error(request, 'הסיסמה החדשה קצרה מדי.')
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'הסיסמה עודכנה בהצלחה.')
            return redirect('admin_dashboard')

    return render(request, 'change_password.html')

@login_required
def create_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'לא ניתן ליצור את המשתמש – שם משתמש זה כבר קיים.')
        else:
            user = CustomUser.objects.create_user(username=username, email=email, password=password, role=role)
            user.save()
            messages.success(request, 'המשתמש נוסף בהצלחה למערכת.')
            return redirect('user_list')

    return render(request, 'create_user.html')

@login_required
def toggle_block(request, user_id):
    if request.user.role != 'admin':
        return render(request, 'not_authorized.html')

    user_to_toggle = get_object_or_404(CustomUser, id=user_id)

    if user_to_toggle != request.user:
        user_to_toggle.is_blocked = not user_to_toggle.is_blocked
        user_to_toggle.save()
        status = 'חסום' if user_to_toggle.is_blocked else 'פעיל'
        messages.success(request, f"הסטטוס של המשתמש עודכן ל: {status}")

    return redirect('user_list')

# ------------------ ניהול בקשות ------------------ #

@login_required
def submit_request(request):
    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.student = request.user
            new_request.save()

            print(f"ערך request_type שהתקבל: {new_request.request_type}")  # שורת בדיקה

            message = (
                f"סטודנט/ית {request.user.get_full_name()} שלח/ה בקשה חדשה.\n\n"
                f"נושא: {new_request.subject}\n"
                f"סוג בקשה: {new_request.get_request_type_display()}\n"
                f"קורס: {new_request.course}\n"
                f"סיבה: {new_request.reason}"
            )

            # --- שלח למרצה רק אם ערעור ציון ---
            if new_request.request_type == 'appeal':  # הערך שהתקבל מהטופס
                print("שולח מייל למרצה!")
                send_mail(
                    subject='בקשה חדשה לערעור ציון',
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['lec2@gmail.com'],
                    fail_silently=False,
                )

            # שליחת מייל למזכירות (קיים אצלך)
            secretary_email = 'sec2@gmail.com'  
            send_mail(
                subject='בקשה חדשה התקבלה במערכת',
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[secretary_email],
                fail_silently=False,
            )

            # יצירת Notification פנימית לכל המזכירות
            secretaries = CustomUser.objects.filter(role='Secretary')
            for sec in secretaries:
                Notification.objects.create(
                    user=sec,
                    message=message,
                )

            return redirect('request_confirmation')
    else:
        form = RequestForm()
    return render(request, 'submit_request.html', {'form': form})


@login_required
def request_confirmation(request):
    return render(request, 'request_confirmation.html')

@login_required
def sample_requests(request):
    return render(request, 'sample_requests.html')



@login_required
def edit_request(request, request_id):
    req = get_object_or_404(Request, pk=request_id, student=request.user)
    now = timezone.now()
    if (now - req.created_at) > timedelta(minutes=10):
        return render(request, 'edit_request.html', {
            'error_message': 'עבור זמן העריכה עבר.'
        })

    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES, instance=req)
        if form.is_valid():
            form.save()
            # מפנים לדף אישור עם הודעה מותאמת
            return redirect('edit_request_confirmation')
    else:
        form = RequestForm(instance=req)

    return render(request, 'edit_request.html', {'form': form})

@login_required
def edit_request_confirmation(request):
    message = "הבקשה עודכנה בהצלחה!"
    return render(request, 'edit_request_confirmation.html', {'message': message})



@login_required
def student_requests(request):
    requests_list = Request.objects.filter(student=request.user)
    now = timezone.now()

    for req in requests_list:
        req.can_edit = (now - req.created_at) <= timedelta(minutes=10)

        # ✨ מחפש את ההודעה הראשונה שכוללת את נושא הבקשה
        note = Notification.objects.filter(user=request.user, message__icontains=req.subject).order_by('-created_at').first()
        if note and "הודעה מהמזכירות:" in note.message:
            req.latest_note = note.message.split("הודעה מהמזכירות:")[-1].strip()
        else:
            req.latest_note = ''

    return render(request, 'student_requests.html', {'requests': requests_list})


@login_required
def student_history(request):
    requests_list = Request.objects.filter(student=request.user).order_by('-created_at')
    return render(request, 'student_history.html', {'requests': requests_list})

@login_required
def requests_admin_list(request):
    if request.user.role not in ['admin', 'secretary']:
        return render(request, 'not_authorized.html')
    requests = Request.objects.all().order_by('-created_at')
    return render(request, 'requests_admin_list.html', {'requests': requests})

@login_required
def student_notifications(request):
    unread_notifications = request.user.notifications.filter(is_read=False)
    all_notifications = request.user.notifications.all().order_by('-created_at')

    # סימון כל ההודעות כנקראו
    unread_notifications.update(is_read=True)

    return render(request, 'student_notifications.html', {
        'notifications': all_notifications,
    })



@login_required
def manage_requests(request):
    if request.user.role not in ['admin', 'secretary']:
        return render(request, 'not_authorized.html')

    requests = Request.objects.all().order_by('-created_at')

    # 🔁 מחשבים את כמות הימים שנותרו
    for r in requests:
        if r.due_date:
            r.remaining_days = (r.due_date - date.today()).days
        else:
            default_due_date = r.created_at.date() + timedelta(days=5)
            r.remaining_days = (default_due_date - date.today()).days

    return render(request, 'manage_requests.html', {
        'requests': requests,
    })


@login_required
def update_request_status(request, request_id):
    if request.method == 'POST':
        req = get_object_or_404(Request, id=request_id)
        new_status = request.POST.get('status')
        message_text = request.POST.get('message', '').strip()

        if new_status in ['submitted', 'in_progress', 'approved', 'rejected']:
            req.status = new_status
            req.save()

            # ✉️ שליחת התראה עם ההודעה שהוזנה
            if message_text:
                Notification.objects.create(
                    user=req.student,
                    message=f"הבקשה שלך '{req.subject}' עודכנה ל־{req.get_status_display()}.\nהודעה מהמזכירה: {message_text}"
                )
            else:
                Notification.objects.create(
                    user=req.student,
                    message=f"הבקשה שלך '{req.subject}' עודכנה ל־{req.get_status_display()}."
                )

            messages.success(request, 'הסטטוס וההודעה נשלחו בהצלחה.')
            return redirect('requests_admin_list')

    return redirect('requests_admin_list')



# ------------------ התראות 🔔 ------------------ #

def send_notification(user, message):
    Notification.objects.create(user=user, message=message)

    

@login_required
def notifications_api(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    notification_list = [n.message for n in notifications]
    return JsonResponse({'notifications': notification_list})

# ------------------ דירוג מערכת ⭐ ------------------ #

@login_required
def submit_rating(request):
    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating'))
        except (TypeError, ValueError):
            rating = 0

        comment = request.POST.get('comment', '')

        if 1 <= rating <= 5:
            Rating.objects.create(
                rating=rating,
                comment=comment
            )
            return render(request, 'submit_rating.html', {
                'success_message': '🙌 הדירוג נשלח בהצלחה!'
            })
        else:
            messages.error(request, 'יש לבחור דירוג בין 1 ל-5 בלבד.')

    return render(request, 'submit_rating.html')



# בסיס הידע של הצ'אט בוט
knowledge_base = {
    'איך מגישים בקשה': 'כדי להגיש בקשה, לחץ על "הגש בקשה" ומלא את הטופס.',
    'איך משנים סיסמה': 'ניתן לשנות סיסמה דרך פרופיל המשתמש שלך.',
    'איך רואים את היסטוריית הבקשות': 'לחץ על "היסטוריית בקשות" בדשבורד.',
    # אפשר להוסיף כאן עוד שאלות ותשובות
}

@csrf_exempt
@login_required
def chatbot_api(request):
    if request.method in ['GET', 'POST']:
        question = request.GET.get('q') or request.POST.get('message', '')
        question = question.strip().lower()

        response = "מצטער, לא מצאתי תשובה לשאלה שלך. נסה לנסח אחרת."
        greetings = ['היי', 'שלום', 'אהלן', 'hi', 'hello']
        thanks = ['תודה', 'thank you', 'תודה רבה']
        bye_words = ['ביי', 'להתראות', 'goodbye', 'bye']

        if any(greet in question for greet in greetings):
            response = "שלום וברוך הבא! 😊 איך אפשר לעזור לך?"
        elif any(thank in question for thank in thanks):
            response = "תמיד כאן לעזור! 🙏 שמחים שהשתמשת ב־CampusFlow."
        elif any(bye in question for bye in bye_words):
            response = "להתראות! 😊 מקווים לראותך שוב."
        else:
            for keyword, answer in knowledge_base.items():
                if keyword in question:
                    response = answer
                    break

        return JsonResponse({'answer': response})



# views.py

from django.shortcuts import redirect

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        new_username = request.POST.get('username')
        new_email = request.POST.get('email')
        new_phone = request.POST.get('phone')

        if not new_username or not new_email:
            messages.error(request, "שם משתמש ואימייל הם שדות חובה.")
        elif new_phone and not new_phone.isdigit():
            messages.error(request, "טלפון חייב להכיל רק מספרים.")
        else:
            user.username = new_username
            user.email = new_email
            user.phone = new_phone
            user.save()
            messages.success(request, "הפרטים עודכנו בהצלחה.")
            return redirect('update_profile')  # ✅ הפניה לאחר עדכון מוצלח

    return render(request, 'update_profile.html')


@login_required
def view_ratings(request):
    ratings = Rating.objects.all()
    return render(request, 'view_ratings.html', {'ratings': ratings})


# users/views.py


def submit_bug(request):
    success = False
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        BugReport.objects.create(user=request.user, title=title, description=description)
        success = True  # מציינת שנשלח בהצלחה
    return render(request, 'submit_bug.html', {'success': success})


# ניהול באגים למנהל
def manage_bugs(request):
    bugs = BugReport.objects.all()
    if request.method == 'POST':
        bug_id = request.POST.get('bug_id')
        new_status = request.POST.get('status')
        bug = BugReport.objects.get(id=bug_id)
        bug.status = new_status
        bug.save()
        return redirect('manage_bugs')
    return render(request, 'manage_bugs.html', {'bugs': bugs})



def lecturer_change_password(request):
    success = False  # ברירת מחדל
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request, "הסיסמה הנוכחית שגויה.")
        elif new_password != confirm_password:
            messages.error(request, "הסיסמה החדשה ואישור הסיסמה אינם תואמים.")
        elif len(new_password) < 6:
            messages.error(request, "הסיסמה החדשה צריכה להכיל לפחות 6 תווים.")
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            success = True
            return redirect('lecturer_dashboard')  # ✅ הפנייה אחרי הצלחה

    return render(request, 'lecturer_change_password.html', {'success': success})


from django.db.models import Count
from django.contrib.auth.decorators import login_required
from .models import Request

@login_required
def request_reports(request):
    if request.user.role != 'secretary':
        return render(request, 'not_authorized.html')

    # סוגי הבקשות בעברית
    request_type_display = dict(Request.REQUEST_TYPES)

    # שליפת מספר בקשות לפי סוג
    raw_data = Request.objects.values('request_type').annotate(total=Count('id'))

    # תרגום סוגים לשמות בעברית
    report_data = [
        {
            'type': request_type_display.get(row['request_type'], row['request_type']),
            'total': row['total']
        }
        for row in raw_data
    ]

    return render(request, 'request_reports.html', {
        'report_data': report_data
    })


from django.db.models import Count
from django.utils.timezone import now
from .models import Request

@login_required
@login_required
def request_summary(request):
    total_requests = Request.objects.count()
    by_status = Request.objects.values('status').annotate(count=Count('id'))
    unique_students = Request.objects.values('student').distinct().count()
    earliest = Request.objects.order_by('created_at').first()
    latest = Request.objects.order_by('-created_at').first()

    return render(request, 'request_summary.html', {
        'total_requests': total_requests,
        'by_status': by_status,
        'unique_students': unique_students,
        'earliest': earliest,
        'latest': latest,
    })

from django.db.models import Count
from django.shortcuts import render
from .models import Request

@login_required
def request_patterns(request):
    # קבוצת נושאים שחוזרים יותר מפעם אחת
    repeated_subjects = (
        Request.objects
        .values('subject')
        .annotate(count=Count('id'))
        .filter(count__gt=1)
        .order_by('-count')
    )

    # סטטיסטיקה לפי סוג בקשה
    type_patterns = (
        Request.objects
        .values('request_type')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    return render(request, 'request_patterns.html', {
        'repeated_subjects': repeated_subjects,
        'type_patterns': type_patterns
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Request, Notification

User = get_user_model()

@login_required
def remind_grade_appeals(request):
    if request.user.role != 'secretary':
        return redirect('not_authorized')

    # שליפת בקשות ערעור שלא טופלו
    appeals = Request.objects.filter(request_type='appeal', status__in=['submitted', 'in_progress'])

    if appeals.exists():
        lecturers = User.objects.filter(role='lecturer')
        for lecturer in lecturers:
            Notification.objects.create(
                user=lecturer,
                message="📢 יש בקשות ערעור ציון שדורשות את הטיפול שלך במערכת."
            )
        messages.success(request, "נשלחה תזכורת למרצה  ✅")
    else:
        messages.info(request, "אין בקשות ערעור ממתינות 📭")

    return redirect('manage_requests')



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Request

@login_required
def lecturer_requests_view(request):
    if request.user.role != 'lecturer':
        return render(request, 'not_authorized.html')

    # הצגת רק בקשות מסוג ערעור ציון
    requests = Request.objects.filter(request_type='appeal').order_by('-created_at')
    return render(request, 'lecturer_requests.html', {'requests': requests})


@login_required
def update_request_status_by_lecturer(request, request_id):
    if request.method == 'POST' and request.user.role == 'lecturer':
        req = get_object_or_404(Request, id=request_id)
        action = request.POST.get('action')
        feedback = request.POST.get('feedback')
        
        if action == 'approve':
            req.status = 'approved'
        elif action == 'reject':
            req.status = 'rejected'
        
        req.lecturer_feedback = feedback
        req.save()

        # יצירת התראה לסטודנט
        Notification.objects.create(
            user=req.student,
            message=f"הבקשה שלך '{req.subject}' עודכנה על ידי המרצה: {req.status.upper()} - {feedback}"
        )

        messages.success(request, "הבקשה עודכנה ✅")
    return redirect('lecturer_requests')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Request
from django.utils.dateparse import parse_date
from django.contrib import messages
from django.db.models import Q  

@login_required
def lecturer_requests_view(request):
    if request.user.role != 'lecturer':
        return redirect('not_authorized')

    selected_status = request.GET.get('status')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    student_name = request.GET.get('student_name', '').strip()  # חדש

    # בקשות מסוג ערעור בלבד
    requests = Request.objects.filter(request_type='appeal')

    # סינון לפי סטטוס
    if selected_status:
        requests = requests.filter(status=selected_status)

    # סינון לפי תאריכים
    if start_date:
        try:
            requests = requests.filter(created_at__date__gte=parse_date(start_date))
        except:
            messages.warning(request, "תאריך התחלה לא תקין")

    if end_date:
        try:
            requests = requests.filter(created_at__date__lte=parse_date(end_date))
        except:
            messages.warning(request, "תאריך סיום לא תקין")

    # --- סינון לפי שם סטודנט (הוספה בלבד!) ---
    if student_name:
        requests = requests.filter(
            Q(student__first_name__icontains=student_name) |
            Q(student__last_name__icontains=student_name) |
            Q(student__username__icontains=student_name)
        )

    context = {
        'requests': requests.order_by('-created_at'),
        'selected_status': selected_status or '',
        'selected_start': start_date or '',
        'selected_end': end_date or '',
        'student_name': student_name,  # העבר ל־template כדי לשמור את הערך
    }

    return render(request, 'lecturer_requests.html', context)

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LecturerProfileForm
from .forms import LecturerProfileForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def lecturer_profile(request):
    user = request.user
    if not hasattr(user, 'role') or user.role != 'lecturer':
        return redirect('not_authorized')

    if request.method == 'POST':
        form = LecturerProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "הפרטים עודכנו בהצלחה!")
            return redirect('lecturer_profile')
        else:
            messages.error(request, "יש שגיאה בעדכון. בדוק את הפרטים ונסה שוב.")
    else:
        form = LecturerProfileForm(instance=user)

    return render(request, 'lecturer_profile.html', {'form': form})

