from django.urls import path
from . import views

urlpatterns = [
    # התחברות והתנתקות
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

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
]
