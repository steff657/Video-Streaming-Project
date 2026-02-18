from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import AdminActionLog, Comment, Profile, Report, Video


class PlatformFeaturesTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='ComplexPass123!',
        )
        self.other = self.User.objects.create_user(
            username='viewer',
            email='viewer@example.com',
            password='ComplexPass123!',
        )
        self.staff = self.User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='ComplexPass123!',
            is_staff=True,
        )

    def _fake_video(self, name='sample.mp4', size=128):
        return SimpleUploadedFile(name, b'0' * size, content_type='video/mp4')

    def test_upload_rejects_invalid_extension(self):
        self.client.login(username='creator', password='ComplexPass123!')
        response = self.client.post(
            reverse('upload_video'),
            {
                'title': 'Bad file',
                'description': 'x',
                'tags': 'tag1',
                'visibility': Video.Visibility.PUBLIC,
                'video_file': SimpleUploadedFile(
                    'bad.txt', b'abc', content_type='text/plain'
                ),
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Video.objects.count(), 0)

    @override_settings(MAX_UPLOAD_SIZE=10)
    def test_upload_rejects_oversized_file(self):
        self.client.login(username='creator', password='ComplexPass123!')
        response = self.client.post(
            reverse('upload_video'),
            {
                'title': 'Big file',
                'description': 'x',
                'tags': 'tag1',
                'visibility': Video.Visibility.PUBLIC,
                'video_file': self._fake_video(size=64),
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Video.objects.count(), 0)

    def test_comment_must_not_be_empty(self):
        video = Video.objects.create(
            owner=self.user,
            title='Test',
            visibility=Video.Visibility.PUBLIC,
            video_file=self._fake_video(),
        )
        self.client.login(username='viewer', password='ComplexPass123!')
        response = self.client.post(
            reverse('post_comment', args=[video.id]),
            {'comment_text': '   '},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Comment.objects.count(), 0)

    def test_profile_can_be_updated(self):
        self.client.login(username='creator', password='ComplexPass123!')
        response = self.client.post(
            reverse('edit_profile'),
            {'display_name': 'Creator Name', 'bio': 'My bio'},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.display_name, 'Creator Name')
        self.assertEqual(profile.bio, 'My bio')

    def test_account_settings_requires_current_password(self):
        self.client.login(username='creator', password='ComplexPass123!')
        response = self.client.post(
            reverse('account_settings'),
            {
                'email': 'newmail@example.com',
                'current_password': 'wrong',
                'new_password': '',
                'confirm_new_password': '',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'creator@example.com')

    def test_account_settings_updates_email_and_password(self):
        self.client.login(username='creator', password='ComplexPass123!')
        response = self.client.post(
            reverse('account_settings'),
            {
                'email': 'newmail@example.com',
                'current_password': 'ComplexPass123!',
                'new_password': 'DifferentPass123!',
                'confirm_new_password': 'DifferentPass123!',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newmail@example.com')
        self.assertTrue(self.user.check_password('DifferentPass123!'))

    def test_user_can_submit_video_report(self):
        video = Video.objects.create(
            owner=self.user,
            title='Reported',
            visibility=Video.Visibility.PUBLIC,
            video_file=self._fake_video(),
        )
        self.client.login(username='viewer', password='ComplexPass123!')
        response = self.client.post(
            reverse('report_video', args=[video.id]),
            {'reason': 'Policy violation'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Report.objects.count(), 1)
        report = Report.objects.first()
        self.assertEqual(report.reporter, self.other)
        self.assertEqual(report.video, video)

    def test_staff_can_delete_reported_video_and_action_is_logged(self):
        video = Video.objects.create(
            owner=self.user,
            title='Reported',
            visibility=Video.Visibility.PUBLIC,
            video_file=self._fake_video(),
        )
        report = Report.objects.create(
            reporter=self.other, video=video, reason='Policy violation'
        )
        self.client.login(username='staff', password='ComplexPass123!')
        response = self.client.post(
            reverse('admin_delete_reported_video', args=[report.id]),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Video.objects.filter(id=video.id).exists())
        report.refresh_from_db()
        self.assertEqual(report.status, Report.Status.RESOLVED)
        self.assertTrue(
            AdminActionLog.objects.filter(
                action=AdminActionLog.Action.DELETE_VIDEO
            ).exists()
        )

    def test_staff_can_delete_user_and_logs_action(self):
        self.client.login(username='staff', password='ComplexPass123!')
        target = self.User.objects.create_user(
            username='to_remove',
            email='remove@example.com',
            password='ComplexPass123!',
        )
        response = self.client.post(
            reverse('admin_delete_user', args=[target.id]),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.User.objects.filter(id=target.id).exists())
        self.assertTrue(
            AdminActionLog.objects.filter(
                action=AdminActionLog.Action.DELETE_USER
            ).exists()
        )

    def test_deploy_health_check_command_passes(self):
        output = StringIO()
        call_command('check_deploy_health', stdout=output)
        self.assertIn('Deployment health check passed', output.getvalue())
