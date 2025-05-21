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
from .models import Request
from django.contrib import messages
from .models import BugReport




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

@login_required
def lecturer_dashboard(request):
    return render(request, 'lecturer_dashboard.html')

@login_required
def secretary_dashboard(request):
    return render(request, 'secretary_dashboard.html')

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
        form = RequestForm(request.POST)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.student = request.user
            new_request.save()
            messages.success(request, 'הבקשה נשלחה בהצלחה!')
            return redirect('student_requests')  # ✅ זה הפתרון!
    else:
        form = RequestForm()

    return render(request, 'submit_request.html', {'form': form})


@login_required
def student_requests(request):
    requests_list = Request.objects.filter(student=request.user)
    return render(request, 'student_requests.html', {'requests': requests_list})

@login_required
def student_history(request):
    requests_list = Request.objects.filter(student=request.user).order_by('-created_at')
    return render(request, 'student_history.html', {'requests': requests_list})

@login_required
def manage_requests(request):
    if request.user.role not in ['admin', 'secretary', 'lecturer']:
        return render(request, 'not_authorized.html')
    all_requests = Request.objects.all().order_by('-created_at')
    return render(request, 'manage_requests.html', {'requests': all_requests})

@login_required
def update_request_status(request, request_id):
    if request.method == 'POST':
        req = get_object_or_404(Request, id=request_id)
        new_status = request.POST.get('status')

        if new_status in ['נשלחה', 'בטיפול', 'אושרה', 'נדחתה']:
            req.status = new_status
            req.save()
            send_notification(req.student, f"הסטטוס של הבקשה '{req.title}' עודכן ל: {new_status}")
            messages.success(request, 'הסטטוס עודכן בהצלחה.')
            return redirect('secretary_dashboard')
    return redirect('secretary_dashboard')

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
            rating = 0  # אם לא נשלח או לא ניתן להמיר

        comment = request.POST.get('comment', '')

        if 1 <= rating <= 5:
            Rating.objects.create(
                rating=rating,
                comment=comment
            )
            messages.success(request, 'תודה שדירגת את השירות! 💬')
            return redirect('student_dashboard')  # ✅ הפניה לאחר שליחה תקינה
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
