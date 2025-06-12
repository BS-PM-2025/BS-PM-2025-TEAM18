from django.contrib import admin
from django.urls import path
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),  # <<-- השורה שחסרה אצלך!

    # 🔐 התחברות, התנתקות, הרשמה
    path('register/', user_views.register_view, name='register'),
    path('login/', user_views.user_login, name='login'),
    path('logout/', user_views.user_logout, name='logout'),

    # 🏠 דף הבית
    path('', user_views.home, name='home'),

    # 📋 דשבורדים לפי תפקיד
    path('admin_dashboard/', user_views.admin_dashboard, name='admin_dashboard'),
    path('student_dashboard/', user_views.student_dashboard, name='student_dashboard'),
    path('lecturer_dashboard/', user_views.lecturer_dashboard, name='lecturer_dashboard'),
    path('secretary_dashboard/', user_views.secretary_dashboard, name='secretary_dashboard'),

    # 👤 עמודים ניהוליים למנהל
    path('admin_dashboard/users/', user_views.user_list, name='user_list'),

    # 🎓 פונקציות לסטודנט
    path('student_dashboard/submit_request/', user_views.submit_request, name='submit_request'),
    path('student_dashboard/requests/', user_views.student_requests, name='student_requests'),
    path('student_dashboard/request_confirmation/', user_views.request_confirmation, name='request_confirmation'),
    path('student_dashboard/sample_requests/', user_views.sample_requests, name='sample_requests'),
    path('student_dashboard/history/', user_views.student_history, name='student_history'),
    path('student_dashboard/edit_request/<int:request_id>/', user_views.edit_request, name='edit_request'),
    path('student_dashboard/edit_request_confirmation/', user_views.edit_request_confirmation, name='edit_request_confirmation'),
    path('student_dashboard/update_profile/', user_views.update_profile, name='update_profile'),  # ✅ הוספתי כאן
    path('student_dashboard/notifications/', user_views.notifications_api, name='notifications_api'),
    path('student_dashboard/submit_rating/', user_views.submit_rating, name='submit_rating'),
    path('student_dashboard/chatbot/', user_views.chatbot_api, name='chatbot_api'),

    # ✏️ מזכירה/מרצה - ניהול בקשות
    path('update_request_status/<int:request_id>/', user_views.update_request_status, name='update_request_status'),
    path('manage_requests/', user_views.manage_requests, name='manage_requests'),
    path('admin_dashboard/view_ratings/', user_views.view_ratings, name='view_ratings'),
    path('admin_dashboard/profile/', user_views.profile_view, name='profile_view'),
    path('admin_dashboard/change_password/', user_views.change_password, name='change_password'),
    path('admin_dashboard/create_user/', user_views.create_user, name='create_user'),
    path('admin_dashboard/toggle_block/<int:user_id>/', user_views.toggle_block, name='toggle_block'),


     path('student_dashboard/submit_bug/', user_views.submit_bug, name='submit_bug'),

    #  ניהול באגים על ידי מנהל
    path('admin_dashboard/manage_bugs/', user_views.manage_bugs, name='manage_bugs'),

    path('lecturer_dashboard/change_password/', user_views.lecturer_change_password, name='lecturer_change_password'),

    path('notification/read/<int:pk>/', user_views.mark_notification_read, name='mark_notification_read'),

      path('manage_requests/', user_views.requests_admin_list, name='manage_requests'),
    path('request/update_status/<int:request_id>/', user_views.update_request_status, name='update_request_status'),
        path('requests_admin_list/', user_views.requests_admin_list, name='requests_admin_list'),
            path('request_reports/', user_views.request_reports, name='request_reports'),
                path('request_summary/', user_views.request_summary, name='request_summary'),
path('request_patterns/', user_views.request_patterns, name='request_patterns'),

    path('remind_grade_appeals/', user_views.remind_grade_appeals, name='remind_grade_appeals'),

    path('lecturer/mark_read/', user_views.mark_notifications_as_read, name='mark_notifications_as_read'),
        path('lecturer/requests/', user_views.lecturer_requests_view, name='lecturer_requests'),

path('lecturer/update_status/<int:request_id>/',  user_views.update_request_status_by_lecturer, name='update_request_status_by_lecturer'),
    path('requests/update/<int:request_id>/',  user_views.update_request_status_by_lecturer, name='update_request_status_by_lecturer'),
# urls.py
path('lecturer/profile/', user_views.lecturer_profile, name='lecturer_profile')

]





