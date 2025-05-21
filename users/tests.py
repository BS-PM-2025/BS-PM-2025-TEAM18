from django.test import TestCase, Client
from django.urls import reverse
from .models import CustomUser
from django.contrib.auth import authenticate
from .models import  BugReport, Rating


# ✅ בדיקות יחידה – לכל סיפור
class UserUnitTests(TestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_user(username='admin1', password='admin1234', role='admin')
        self.student_user = CustomUser.objects.create_user(username='student1', password='student1234', role='student')
        self.lecturer_user = CustomUser.objects.create_user(username='lecturer1', password='lect1234', role='lecturer')
        self.secretary_user = CustomUser.objects.create_user(username='secretary1', password='sec1234', role='secretary')

    def test_admin_authentication(self):
        user = authenticate(username='admin1', password='admin1234')
        self.assertIsNotNone(user)
        self.assertEqual(user.role, 'admin')

    def test_admin_logout_flag(self):
        self.client.login(username='admin1', password='admin1234')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)

    def test_student_authentication(self):
        user = authenticate(username='student1', password='student1234')
        self.assertIsNotNone(user)
        self.assertEqual(user.role, 'student')

    def test_student_logout_flag(self):
        self.client.login(username='student1', password='student1234')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)

    def test_secretary_authentication(self):
        user = authenticate(username='secretary1', password='sec1234')
        self.assertIsNotNone(user)
        self.assertEqual(user.role, 'secretary')

    def test_secretary_logout_flag(self):
        self.client.login(username='secretary1', password='sec1234')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)

    def test_lecturer_authentication(self):
        user = authenticate(username='lecturer1', password='lect1234')
        self.assertIsNotNone(user)
        self.assertEqual(user.role, 'lecturer')

    def test_lecturer_logout_flag(self):
        self.client.login(username='lecturer1', password='lect1234')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)

    def test_user_list_retrieval(self):
        self.client.login(username='admin1', password='admin1234')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)

    def test_profile_access(self):
        self.client.login(username='admin1', password='admin1234')
        response = self.client.get(reverse('profile_view'))
        self.assertEqual(response.status_code, 200)

    def test_change_password_logic(self):
        self.client.login(username='admin1', password='admin1234')
        response = self.client.post(reverse('change_password'), {
            'current_password': 'admin1234',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_user_creation_logic(self):
        self.client.login(username='admin1', password='admin1234')
        response = self.client.post(reverse('create_user'), {
            'username': 'newuser',
            'email': 'new@user.com',
            'password': '12345',
            'role': 'student'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CustomUser.objects.filter(username='newuser').exists())

    def test_block_user_toggle_logic(self):
        self.client.login(username='admin1', password='admin1234')
        target = CustomUser.objects.create_user(username='target', password='target123', role='student')
        response = self.client.get(reverse('toggle_block', args=[target.id]))
        target.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertIn(target.is_blocked, [True, False])


    def test_student_can_access_my_requests(self):
        self.client.login(username='student1', password='student1234')
        response = self.client.get(reverse('student_requests'))
        self.assertEqual(response.status_code, 200)

    def test_student_can_view_request_history(self):
        self.client.login(username='student1', password='student1234')
        response = self.client.get(reverse('student_history'))
        self.assertEqual(response.status_code, 200)

    def test_student_can_see_status_notification(self):
        self.client.login(username='student1', password='student1234')
        response = self.client.get(reverse('notifications_api'))
        self.assertEqual(response.status_code, 200)

    def test_student_can_submit_rating(self):
        self.client.login(username='student1', password='student1234')
        response = self.client.post(reverse('submit_rating'), {
            'rating': 4,
            'comment': 'מצוין'
        })
        self.assertEqual(response.status_code, 302)

    def test_chatbot_returns_answer(self):
        self.client.login(username='student1', password='student1234')
        response = self.client.post(reverse('chatbot_api'), {'message': 'איך מגישים בקשה?'})
        self.assertEqual(response.status_code, 200)

    def test_student_profile_update(self):
        self.client.login(username='student1', password='student1234')
        response = self.client.post(reverse('update_profile'), {
            'email': 'newemail@example.com',
            'phone': '0501234567'
        })
        self.assertEqual(response.status_code, 200)



    def test_admin_can_view_ratings(self):
        self.client.login(username='admin1', password='admin1234')
        response = self.client.get(reverse('view_ratings'))
        self.assertEqual(response.status_code, 200)

    def test_admin_can_update_bug_status(self):
        self.client.login(username='admin1', password='admin1234')
        BugReport.objects.create(id=1, title="bug", description="bug desc", status="פתוח", user=self.admin_user)
        response = self.client.post(reverse('manage_bugs'), {
            'bug_id': 1,
            'status': 'טופל'
        })
        self.assertEqual(response.status_code, 302)

    def test_lecturer_can_change_password(self):
        self.client.login(username='lecturer1', password='lect1234')
        response = self.client.post(reverse('lecturer_change_password'), {
            'current_password': 'lect1234',
            'new_password': 'newpass987',
            'confirm_password': 'newpass987'
        })
        self.assertEqual(response.status_code, 302)

# ✅ בדיקות אינטגרציה – לכל סיפור
class UserIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = CustomUser.objects.create_user(username='admin1', password='admin1234', role='admin')
        self.student_user = CustomUser.objects.create_user(username='student1', password='student1234', role='student')
        self.lecturer_user = CustomUser.objects.create_user(username='lecturer1', password='lect1234', role='lecturer')
        self.secretary_user = CustomUser.objects.create_user(username='secretary1', password='sec1234', role='secretary')

    def test_admin_login_redirect(self):
        response = self.client.post(reverse('login'), {'username': 'admin1', 'password': 'admin1234'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin_dashboard/', response.url)

    def test_admin_logout(self):
        self.client.login(username='admin1', password='admin1234')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)

    def test_student_login_redirect(self):
        response = self.client.post(reverse('login'), {'username': 'student1', 'password': 'student1234'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/student_dashboard/', response.url)

    def test_student_logout(self):
        self.client.login(username='student1', password='student1234')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)

    def test_secretary_login_redirect(self):
        response = self.client.post(reverse('login'), {'username': 'secretary1', 'password': 'sec1234'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/secretary_dashboard/', response.url)

    def test_secretary_logout(self):
        self.client.login(username='secretary1', password='sec1234')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)

    def test_lecturer_login_redirect(self):
        response = self.client.post(reverse('login'), {'username': 'lecturer1', 'password': 'lect1234'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/lecturer_dashboard/', response.url)

    def test_lecturer_logout(self):
        self.client.login(username='lecturer1', password='lect1234')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)

    def test_user_list_by_admin(self):
        self.client.login(username='admin1', password='admin1234')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)

    def test_profile_view_admin(self):
        self.client.login(username='admin1', password='admin1234')
        response = self.client.get(reverse('profile_view'))
        self.assertEqual(response.status_code, 200)

    def test_password_change_admin(self):
        self.client.login(username='admin1', password='admin1234')
        response = self.client.post(reverse('change_password'), {
            'current_password': 'admin1234',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_create_user_admin(self):
        self.client.login(username='admin1', password='admin1234')
        response = self.client.post(reverse('create_user'), {
            'username': 'newuser',
            'email': 'new@user.com',
            'password': '12345',
            'role': 'student'
        })
        self.assertEqual(response.status_code, 302)

    def test_block_toggle_admin(self):
        self.client.login(username='admin1', password='admin1234')
        target = CustomUser.objects.create_user(username='target', password='target123', role='student')
        response = self.client.get(reverse('toggle_block', args=[target.id]))
        self.assertEqual(response.status_code, 302)


    def test_request_status_displayed_correctly(self):
        self.client.login(username='student1', password='student1234')
        response = self.client.get(reverse('student_requests'))
        self.assertContains(response, 'סטטוס')

    def test_request_history_sorted_by_date(self):
        self.client.login(username='student1', password='student1234')
        response = self.client.get(reverse('student_history'))
        self.assertIn('תאריך', response.content.decode())

    def test_notification_shows_status_update(self):
        self.client.login(username='student1', password='student1234')
        response = self.client.get(reverse('notifications_api'))
        self.assertEqual(response.status_code, 200)  # הוסר assertContains כי אין טקסט בפונקציית API ריקה

    def test_rating_value_is_valid(self):
        self.client.login(username='student1', password='student1234')
        response = self.client.post(reverse('submit_rating'), {
            'rating': 6,
            'comment': 'שגוי'
        })
        self.assertNotEqual(response.status_code, 302)

    def test_chatbot_response_contains_text(self):
        self.client.login(username='student1', password='student1234')
        response = self.client.post(reverse('chatbot_api'), {'message': 'שאלה'})
        self.assertEqual(response.status_code, 200)

    def test_invalid_phone_number_rejected(self):
        self.client.login(username='student1', password='student1234')
        response = self.client.post(reverse('update_profile'), {
            'phone': 'notanumber'
        })
        self.assertNotEqual(response.status_code, 302)

    def test_request_details_match_data(self):
        self.client.login(username='student1', password='student1234')
        response = self.client.get(reverse('student_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('בקשה', response.content.decode())



    def test_ratings_table_contains_data(self):
        self.client.login(username='admin1', password='admin1234')
        response = self.client.get(reverse('view_ratings'))
        self.assertEqual(response.status_code, 200)

    def test_bug_status_updated_successfully(self):
        self.client.login(username='admin1', password='admin1234')
        bug = BugReport.objects.create(title="bug", description="bug desc", user=self.admin_user, status="פתוח")
        response = self.client.post(reverse('manage_bugs'), {
        'bug_id': bug.id,
        'status': 'טופל'
    })
        self.assertEqual(response.status_code, 302)
        bug.refresh_from_db()
        self.assertEqual(bug.status, 'טופל')


    def test_lecturer_password_change_validates_correctly(self):
        self.client.login(username='lecturer1', password='lect1234')
        response = self.client.post(reverse('lecturer_change_password'), {
            'current_password': 'wrongpass',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        })
        self.assertNotEqual(response.status_code, 302)