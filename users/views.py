from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from django.contrib.auth import get_user_model

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
                role='student'  # ✅ נרשם רק כסטודנט
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
            messages.error(request, 'הסיסמה החדשה קצרה מדי. אנא הזן לפחות 6 תווים.')
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


# ✅ חסימת משתמש – סיפור 13
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


# ✅ דף הבית
def home(request):
    return render(request, 'home.html')
