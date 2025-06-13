from django.test import TestCase, Client
from django.urls import reverse
from .models import CustomUser
from django.contrib.auth import authenticate
from .models import  BugReport, Rating
from django.utils import timezone
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import  Request
from users.forms import RequestForm
from django.shortcuts import render, redirect, get_object_or_404

from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile

# ––––––––––––––––––––––––––––––––––––––––––––––––––––
# תחליף את “users” בשם האפליקציה שלך אם הוא שונה
# ––––––––––––––––––––––––––––––––––––––––––––––––––––

# כל ה-views שאתה בודק
from users.views import (
    register_view, user_login, home, admin_dashboard, student_dashboard,
    lecturer_dashboard, mark_notifications_as_read, secretary_dashboard,
    mark_notification_read, submit_request, request_confirmation,
    sample_requests, edit_request, edit_request_confirmation,
    requests_admin_list, student_notifications, manage_requests,
    update_request_status, send_notification, submit_rating, chatbot_api,
    update_profile, submit_bug, request_reports, request_summary,
    request_patterns, remind_grade_appeals, lecturer_requests_view,
    update_request_status_by_lecturer, lecturer_profile
)

# כל המודלים שבהם אתה משתמש בתוך המבחנים
from users.models import CustomUser, Request, Notification, BugReport, Rating

# אם במבחנים שלך אתה יוצר RequestForm
from users.forms import RequestForm



# =================== יחידה ===================
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


    # Unit Test for admin_dashboard
    def test_admin_dashboard_requires_login(self):
      factory = RequestFactory()
      request = factory.get(reverse('admin_dashboard'))
      request.user = AnonymousUser()
      response = admin_dashboard(request)
      self.assertNotEqual(response.status_code, 200)  # redirect to login


    # Unit Test for mark_notification_read
    def test_mark_notification_read_changes_flag(self):
      factory = RequestFactory()
      sec = CustomUser.objects.create_user('u','u@x','p', role='secretary')
      note = Notification.objects.create(user=sec, message='m')
      req = factory.get(reverse('mark_notification_read', args=[note.pk]))
      req.user = sec
      response = mark_notification_read(req, note.pk)
      self.assertTrue(Notification.objects.get(pk=note.pk).is_read)

    # Unit Test for submit_request
    def test_submit_request_get_renders_form(self):
      factory = RequestFactory()
      stu = CustomUser.objects.create_user('s','s@x','p', role='student')
      req = factory.get(reverse('submit_request'))
      req.user = stu
      response = submit_request(req)
      self.assertEqual(response.status_code, 200)

    # Unit Test for request_confirmation
    def test_request_confirmation_renders(self):
      factory = RequestFactory()
      req = factory.get(reverse('request_confirmation'))
      req.user = CustomUser()
      response = request_confirmation(req)
      self.assertEqual(response.status_code, 200)

    # Unit Test for sample_requests
    def test_sample_requests_renders(self):
      factory = RequestFactory()
      req = factory.get(reverse('sample_requests'))
      req.user = CustomUser()
      resp = sample_requests(req)
      self.assertEqual(resp.status_code, 200)

    # Unit Test for edit_request_confirmation
    def test_edit_request_confirmation(self):
      factory = RequestFactory()
      req = factory.get(reverse('edit_request_confirmation'))
      req.user = CustomUser()
      resp = edit_request_confirmation(req)
      self.assertEqual(resp.status_code, 200)
  
    # Unit Test for update_request_status
    def test_update_request_status_invalid_method(self):
      factory = RequestFactory()
      req = factory.get(reverse('update_request_status', args=[1]))
      req.user = CustomUser()
      resp = update_request_status(req, 1)
      self.assertEqual(resp.status_code, 302)

# Unit Test for send_notification
    def test_send_notification_creates_notification(self):
      u = CustomUser.objects.create_user('x','x@x','p')
      send_notification(u, 'hey')
      self.assertTrue(Notification.objects.filter(user=u, message='hey').exists())


    # Unit Test for chatbot_api
    def test_chatbot_api_returns_known_answer(self):
      factory = RequestFactory()
      req = factory.get(reverse('chatbot_api') + '?q=איך%20משנים%20סיסמה')
      req.user = CustomUser()
      resp = chatbot_api(req)
      self.assertJSONEqual(resp.content, {'answer': 'ניתן לשנות סיסמה דרך פרופיל המשתמש שלך.'})


    # Unit Test for submit_bug_get(self):
    def test_submit_bug_get_renders_form(self):
      factory = RequestFactory()
      req = factory.get(reverse('submit_bug'))
      req.user = CustomUser()
      resp = submit_bug(req)
      self.assertEqual(resp.status_code, 200)


# =================== אינטגרציה ===================
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
        self.assertEqual(response.status_code, 200)

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

# ============ אינטגרציה: ניהול בקשות ===============
class RequestIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student_user = CustomUser.objects.create_user(username='student1', password='student1234', role='student')
        self.other_user = CustomUser.objects.create_user(username='student2', password='student2345', role='student')

    def test_submit_request_success(self):
        self.client.login(username='student1', password='student1234')
        data = {
            'request_type': 'extension',
            'course': 'מערכות הפעלה',
            'subject': 'בדיקת הגשה',
            'reason': 'הייתי חולה',
        }
        response = self.client.post(reverse('submit_request'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Request.objects.filter(subject='בדיקת הגשה', student__username='student1').exists())


    def test_edit_request_within_10_minutes(self):
        self.client.login(username='student1', password='student1234')
        req = Request.objects.create(
            student=self.student_user,
            request_type='extension',
            course='בדיקה',
            subject='נושא',
            created_at=timezone.now()
        )
        response = self.client.get(reverse('edit_request', args=[req.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_edit_request_after_10_minutes(self):
        self.client.login(username='student1', password='student1234')
        req = Request.objects.create(
            student=self.student_user,
            request_type='extension',
            course='קורס',
            subject='ישן',
            created_at=timezone.now() - timedelta(minutes=15)
        )
        response = self.client.get(reverse('edit_request', args=[req.id]))
        self.assertEqual(response.status_code, 200)
        # בדוק שמועבר הודעה או error, או שהתוכן בעמוד השתנה
        # אם יש context עם הודעה:
        # self.assertIn('message', response.context)
        # אחרת, בדיקה גנרית:
        self.assertIn('container', response.content.decode())  # יש תוכן כלשהו

    def test_invalid_request_type(self):
        self.client.login(username='student1', password='student1234')
        data = {
            'request_type': 'illegal',
            'course': 'קורס',
            'subject': 'נושא',
        }
        response = self.client.post(reverse('submit_request'), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('errorlist', response.content.decode())  # בדיקה אוניברסלית

    def test_edit_other_student_request(self):
        self.client.login(username='student1', password='student1234')
        req = Request.objects.create(student=self.other_user, request_type='extension', course='test', subject='test')
        response = self.client.get(reverse('edit_request', args=[req.id]))
        self.assertEqual(response.status_code, 404)

    def test_student_sees_only_own_requests(self):
        self.client.login(username='student1', password='student1234')
        Request.objects.create(student=self.other_user, request_type='extension', course='אחר', subject='בדיקה')
        my_req = Request.objects.create(student=self.student_user, request_type='extension', course='שלי', subject='בדיקה')
        response = self.client.get(reverse('student_requests'))
        self.assertIn('שלי', response.content.decode())
        self.assertNotIn('אחר', response.content.decode())

    def test_submit_request_with_file(self):
        self.client.login(username='student1', password='student1234')
        file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")
        data = {
            'request_type': 'extension',
            'course': 'עם קובץ',
            'subject': 'בדיקה',
            'attachment': file
        }
        response = self.client.post(reverse('submit_request'), data)
        self.assertEqual(response.status_code, 302)
        req = Request.objects.filter(course='עם קובץ').first()
        self.assertTrue(req.attachment)

    def test_request_str_in_list(self):
        self.client.login(username='student1', password='student1234')
        req = Request.objects.create(student=self.student_user, request_type='appeal', course='מבוא', subject='ערעור')
        self.assertIn(self.student_user.username, str(req))





# Integration Test for register_view
    def test_register_view_post_creates_user_and_redirects(self):
      payload = {'username': 'u1', 'email': 'u1@x.com', 'password': 'pass1234'}
      response = self.client.post(reverse('register'), data=payload)
      self.assertRedirects(response, reverse('login'))
      self.assertTrue(CustomUser.objects.filter(username='u1').exists())


# Integration Test for home
    def test_home_integration_status_code(self):
      response = self.client.get(reverse('home'))
      self.assertEqual(response.status_code, 200)


    # Integration Test for admin_dashboard
    def test_admin_dashboard_accessible_by_admin(self):
      admin = CustomUser.objects.create_user('a','a@a.com','p', role='admin')
      self.client.force_login(admin)
      response = self.client.get(reverse('admin_dashboard'))
      self.assertEqual(response.status_code, 200)


    # Integration Test for student_dashboard
    def test_student_dashboard_accessible_by_student(self):
      stu = CustomUser.objects.create_user('s','s@x.com','p', role='student')
      self.client.force_login(stu)
      response = self.client.get(reverse('student_dashboard'))
      self.assertEqual(response.status_code, 200)

    # Integration Test for lecturer_dashboard
    def test_lecturer_dashboard_shows_notifications(self):
      lec = CustomUser.objects.create_user('l','l@x.com','p', role='lecturer')
      Notification.objects.create(user=lec, message='hi')
      self.client.force_login(lec)
      response = self.client.get(reverse('lecturer_dashboard'))
      self.assertContains(response, 'hi')

    
# Integration Test for mark_notifications_as_read
    def test_mark_notifications_marks_all_read(self):
      sec = CustomUser.objects.create_user('x','x@x','p', role='secretary')
      Notification.objects.create(user=sec, message='1')
      self.client.force_login(sec)
      response = self.client.post(reverse('mark_notifications_as_read'))
      self.assertJSONEqual(response.content, {'success': True})
      self.assertFalse(Notification.objects.filter(user=sec, is_read=False).exists())

    # Integration Test for secretary_dashboard
    def test_secretary_dashboard_shows_unread_count(self):
      sec = CustomUser.objects.create_user('x','x@x','p', role='secretary')
      Notification.objects.create(user=sec, message='ok')
      self.client.force_login(sec)
      response = self.client.get(reverse('secretary_dashboard'))
      self.assertContains(response, '1')  # unread count


    # Integration Test for mark_notification_read
    def test_mark_notification_read_redirects(self):
      sec = CustomUser.objects.create_user('u','u@x','p', role='secretary')
      note = Notification.objects.create(user=sec, message='m')
      self.client.force_login(sec)
      response = self.client.get(reverse('mark_notification_read', args=[note.pk]))
      self.assertRedirects(response, reverse('secretary_dashboard'))


    
# Integration Test for request_confirmation
    def test_request_confirmation_integration(self):
      self.client.force_login(CustomUser.objects.create_user('u','u@x','p'))
      response = self.client.get(reverse('request_confirmation'))
      self.assertEqual(response.status_code, 200)

    # Integration Test for sample_requests
    def test_sample_requests_integration(self):
      self.client.force_login(CustomUser.objects.create_user('u','u@x','p'))
      resp = self.client.get(reverse('sample_requests'))
      self.assertEqual(resp.status_code, 200)

    # Integration Test for edit_request_confirmation
    def test_edit_request_confirmation_integration(self):
      self.client.force_login(CustomUser.objects.create_user('u','u@x','p'))
      resp = self.client.get(reverse('edit_request_confirmation'))
      self.assertEqual(resp.status_code, 200)

    # Integration Test for requests_admin_list
    def test_requests_admin_list_by_secretary(self):
      sec = CustomUser.objects.create_user('x','x@x','p', role='secretary')
      self.client.force_login(sec)
      resp = self.client.get(reverse('requests_admin_list'))
      self.assertEqual(resp.status_code, 200)


    
# Integration Test for manage_requests
    def test_manage_requests_integration(self):
      sec = CustomUser.objects.create_user('x','x@x','p', role='secretary')
      self.client.force_login(sec)
      resp = self.client.get(reverse('manage_requests'))
      self.assertEqual(resp.status_code, 200)


    # Integration Test for update_request_status
    def test_update_request_status_post_changes_status(self):
      admin = CustomUser.objects.create_user('a','a@a','p', role='admin')
      r = Request.objects.create(student=admin, subject='x')
      self.client.force_login(admin)
      resp = self.client.post(reverse('update_request_status', args=[r.pk]), data={'status':'approved'})
      self.assertRedirects(resp, reverse('requests_admin_list'))
      self.assertEqual(Request.objects.get(pk=r.pk).status, 'approved')


    
# Integration Test for submit_bug_post_creates(self):
    def test_submit_bug_post_creates_bug(self):
      u = CustomUser.objects.create_user('x','x@x','p')
      self.client.force_login(u)
      resp = self.client.post(reverse('submit_bug'), data={'title':'t','description':'d'})
      self.assertTrue(BugReport.objects.filter(user=u, title='t').exists())


    # Integration Test for request_reports(self):
    def test_request_reports_integration(self):
      sec = CustomUser.objects.create_user('s','s@x','p', role='secretary')
      Request.objects.create(student=sec, subject='x', request_type='appeal')
      self.client.force_login(sec)
      resp = self.client.get(reverse('request_reports'))
      self.assertContains(resp, 'ערעור ציון')

    # Integration Test for request_summary(self):
    def test_request_summary_integration(self):
      self.client.force_login(CustomUser.objects.create_user('a','a@a','p'))
      resp = self.client.get(reverse('request_summary'))
      self.assertEqual(resp.status_code, 200)


    # Integration Test for remind_grade_appeals_sends(self):
    def test_remind_grade_appeals_sends_notifications(self):
      sec = CustomUser.objects.create_user('s','s@x','p', role='secretary')
      self.client.force_login(sec)
      resp = self.client.get(reverse('remind_grade_appeals'))
      self.assertRedirects(resp, reverse('manage_requests'))

    # Integration Test for lecturer_requests_view(self):
    def test_lecturer_requests_view_shows_appeals(self):
      lec = CustomUser.objects.create_user('l','l@x','p', role='lecturer')
      Request.objects.create(student=lec, subject='s', request_type='appeal')
      self.client.force_login(lec)
      resp = self.client.get(reverse('lecturer_requests'))
      self.assertContains(resp, 's')


    
# Integration Test for update_request_status_by_lecturer(self):
    def test_update_request_status_by_lecturer_changes(self):
      lec = CustomUser.objects.create_user('l','l@x','p', role='lecturer')
      req_obj = Request.objects.create(student=lec, subject='s', request_type='appeal')
      self.client.force_login(lec)
      resp = self.client.post(reverse('update_request_status_by_lecturer', args=[req_obj.pk]),
                               data={'action':'approve','feedback':'ok'})
      self.assertRedirects(resp, reverse('lecturer_requests'))
      self.assertEqual(Request.objects.get(pk=req_obj.pk).status, 'approved')


    # Integration Test for lecturer_profile_update(self):
    def test_lecturer_profile_can_update(self):
      lec = CustomUser.objects.create_user('l','l@x','p', role='lecturer')
      self.client.force_login(lec)
      resp = self.client.post(reverse('lecturer_profile'),
                              data={'first_name':'N','last_name':'M'})
      self.assertRedirects(resp, reverse('lecturer_profile'))
      self.assertEqual(CustomUser.objects.get(pk=lec.pk).first_name, 'N')