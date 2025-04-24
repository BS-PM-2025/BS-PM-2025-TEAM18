from django.contrib import admin
from django.urls import path, include
from users import views as user_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', user_views.register_view, name='register'),

    path('', include('users.urls')),  # login, logout
    path('', user_views.home, name='home'),  # ⬅️ דף הבית 


    # דשבורדים לפי role:
    path('admin_dashboard/', user_views.admin_dashboard, name='admin_dashboard'),
    path('student_dashboard/', user_views.student_dashboard, name='student_dashboard'),
    path('lecturer_dashboard/', user_views.lecturer_dashboard, name='lecturer_dashboard'),
    path('secretary_dashboard/', user_views.secretary_dashboard, name='secretary_dashboard'),
    

    # עמוד הצגת המשתמשים למנהל
    path('admin_dashboard/users/', user_views.user_list, name='user_list'),
]
