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
    path('student_dashboard/request_confirmation/', views.request_confirmation, name='request_confirmation'),

    path('student_dashboard/requests/', views.student_requests, name='student_requests'),
    path('student_dashboard/history/', views.student_history, name='student_history'),
        path('student_dashboard/sample_requests/', views.sample_requests, name='sample_requests'),
            path('student_dashboard/edit_request/<int:request_id>/', views.edit_request, name='edit_request'),
path('student_dashboard/edit_request_confirmation/', views.edit_request_confirmation, name='edit_request_confirmation'),



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

# users/urls.py
path('notification/read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),

 path('manage_requests/', views.requests_admin_list, name='manage_requests'),
path('request/update_status/<int:request_id>/', views.update_request_status, name='update_request_status'),

    path('requests_admin_list/', views.requests_admin_list, name='requests_admin_list'),
    path('request_reports/', views.request_reports, name='request_reports'),

    path('request_summary/', views.request_summary, name='request_summary'),

path('request_patterns/', views.request_patterns, name='request_patterns'),

    path('remind_grade_appeals/', views.remind_grade_appeals, name='remind_grade_appeals'),

    path('lecturer/mark_read/', views.mark_notifications_as_read, name='mark_notifications_as_read'),

    path('lecturer/requests/', views.lecturer_requests_view, name='lecturer_requests'),
    path('lecturer/update_status/<int:request_id>/', views.update_request_status_by_lecturer, name='update_request_status_by_lecturer'),
    path('requests/update/<int:request_id>/', views.update_request_status_by_lecturer, name='update_request_status_by_lecturer'),
path('lecturer/profile/', views.lecturer_profile, name='lecturer_profile')


]




