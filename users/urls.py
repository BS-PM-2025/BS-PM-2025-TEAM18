from django.urls import path, include
from . import views


urlpatterns = [
      path('', views.home, name='home'),  # דף הבית (לא דף התחברות)
    
      path('', include('users.urls')),  # צריך לכלול את זה!

    path('login/', views.user_login, name='login'),  # דף התחברות
    path('logout/', views.user_logout, name='logout'),  # דף התנתקות

    # דשבורדים לפי תפקיד
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('lecturer_dashboard/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('secretary_dashboard/', views.secretary_dashboard, name='secretary_dashboard'),

    # צפייה ברשימת המשתמשים (סיפור 9)
    path('admin_dashboard/users/', views.user_list, name='user_list'),

    # צפייה בפרטי החשבון שלי (סיפור 10)
    path('admin_dashboard/profile/', views.profile_view, name='profile'),

    # שינוי סיסמה (סיפור 11)
    path('admin_dashboard/change_password/', views.change_password, name='change_password'),

    # יצירת משתמש חדש (סיפור 12)
    path('admin_dashboard/create_user/', views.create_user, name='create_user'),

    # חסימת/שחרור משתמש (סיפור 13)
    path('admin_dashboard/toggle_block/<int:user_id>/', views.toggle_block, name='toggle_block'),

    # 📚 בקשות סטודנט
    path('student_dashboard/submit_request/', views.submit_request, name='submit_request'),
    path('student_dashboard/requests/', views.student_requests, name='student_requests'),
    path('student_dashboard/history/', views.student_history, name='student_history'),

    # 🔔 התראות סטודנט (פעמון)
    path('student_dashboard/notifications/', views.notifications_api, name='notifications_api'),

    # שינוי סטטוס בקשה
path('update_request_status/<int:request_id>/', views.update_request_status, name='update_request_status'),
# דף ניהול בקשות למזכירה/מרצה
path('manage_requests/', views.manage_requests, name='manage_requests'),

path('student_dashboard/submit_rating/', views.submit_rating, name='submit_rating'),


path('student_dashboard/chatbot/', views.chatbot_api, name='chatbot_api'),

# urls.py


path('update_profile/', views.update_profile, name='update_profile'),
# users/urls.py

path('submit_bug/', views.submit_bug, name='submit_bug'),
path('admin_dashboard/manage_bugs/', views.manage_bugs, name='manage_bugs'),


# users/urls.py או איפה שיש לך
path('lecturer_dashboard/change_password/',views.lecturer_change_password, name='lecturer_change_password'),


]
