import datetime
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from .models import Message
from .forms import MessageCreateForm, MessageEditForm


class MessageModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='password123')

    def test_message_str(self):
        msg = Message.objects.create(
            user=self.user,
            title="Graduation Letter",
            content="Congratulations on graduating!",
            unlock_date=timezone.localdate() + datetime.timedelta(days=365)
        )
        self.assertEqual(str(msg), "Graduation Letter")

    def test_future_message_is_locked(self):
        future_date = timezone.localdate() + datetime.timedelta(days=10)
        msg = Message.objects.create(
            user=self.user,
            title="Future Note",
            content="Secret future thoughts",
            unlock_date=future_date
        )
        self.assertTrue(msg.is_locked())
        self.assertFalse(msg.is_unlocked())
        self.assertEqual(msg.days_until_unlock(), 10)

    def test_past_message_is_unlocked(self):
        past_date = timezone.localdate() - datetime.timedelta(days=5)
        msg = Message.objects.create(
            user=self.user,
            title="Past Note",
            content="Unlocked reflections",
            unlock_date=past_date
        )
        self.assertFalse(msg.is_locked())
        self.assertTrue(msg.is_unlocked())
        self.assertEqual(msg.days_until_unlock(), 0)

    def test_today_message_is_unlocked(self):
        today = timezone.localdate()
        msg = Message.objects.create(
            user=self.user,
            title="Today Note",
            content="Available today",
            unlock_date=today
        )
        self.assertFalse(msg.is_locked())
        self.assertTrue(msg.is_unlocked())
        self.assertEqual(msg.days_until_unlock(), 0)


class MessageFormTests(TestCase):
    def test_create_form_valid_with_future_date(self):
        tomorrow = timezone.localdate() + datetime.timedelta(days=1)
        form = MessageCreateForm(data={
            'title': 'Letter to Tomorrow',
            'content': 'Hope tomorrow goes well!',
            'unlock_date': tomorrow
        })
        self.assertTrue(form.is_valid())

    def test_create_form_invalid_with_today(self):
        today = timezone.localdate()
        form = MessageCreateForm(data={
            'title': 'Letter for Today',
            'content': 'This should fail validation.',
            'unlock_date': today
        })
        self.assertFalse(form.is_valid())
        self.assertIn('unlock_date', form.errors)
        self.assertIn('The unlock date must be in the future.', form.errors['unlock_date'])

    def test_create_form_invalid_with_past_date(self):
        yesterday = timezone.localdate() - datetime.timedelta(days=1)
        form = MessageCreateForm(data={
            'title': 'Letter for Yesterday',
            'content': 'Past date should fail.',
            'unlock_date': yesterday
        })
        self.assertFalse(form.is_valid())
        self.assertIn('unlock_date', form.errors)

    def test_edit_form_excludes_unlock_date(self):
        form = MessageEditForm()
        self.assertIn('title', form.fields)
        self.assertIn('content', form.fields)
        self.assertNotIn('unlock_date', form.fields)


class AuthenticationAndSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='bob', password='password123')

    def test_login_required_redirects(self):
        urls = [
            reverse('dashboard'),
            reverse('message_list'),
            reverse('message_create'),
            reverse('message_detail', kwargs={'pk': 1}),
            reverse('message_edit', kwargs={'pk': 1}),
            reverse('message_delete', kwargs={'pk': 1}),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse('login'), response.url)

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'SecretPass123!',
            'password2': 'SecretPass123!',
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login_and_logout(self):
        # Login
        response = self.client.post(reverse('login'), {
            'username': 'bob',
            'password': 'password123',
        })
        self.assertRedirects(response, reverse('dashboard'))

        # Logout
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('home'))


class MessageViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')

        # User1 messages
        self.future_date = timezone.localdate() + datetime.timedelta(days=30)
        self.past_date = timezone.localdate() - datetime.timedelta(days=10)

        self.locked_msg = Message.objects.create(
            user=self.user1,
            title="Super Secret Future Message",
            content="TOP_SECRET_CONTENT_12345",
            unlock_date=self.future_date
        )

        self.unlocked_msg = Message.objects.create(
            user=self.user1,
            title="Old Memory Revealed",
            content="REVEALED_MEMORIES_67890",
            unlock_date=self.past_date
        )

    def test_dashboard_displays_correct_counts(self):
        self.client.login(username='user1', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_count'], 2)
        self.assertEqual(response.context['locked_count'], 1)
        self.assertEqual(response.context['unlocked_count'], 1)

    def test_create_message_view(self):
        self.client.login(username='user1', password='password123')
        unlock_target = timezone.localdate() + datetime.timedelta(days=100)
        response = self.client.post(reverse('message_create'), {
            'title': 'A Future Milestone',
            'content': 'Aiming to be a senior developer!',
            'unlock_date': unlock_target.strftime('%Y-%m-%d')
        })
        self.assertRedirects(response, reverse('message_list'))
        created = Message.objects.filter(title='A Future Milestone').first()
        self.assertIsNotNone(created)
        self.assertEqual(created.user, self.user1)
        self.assertEqual(created.unlock_date, unlock_target)

    def test_locked_message_detail_never_exposes_content(self):
        """
        CRITICAL SECURITY REQUIREMENT:
        Content of a locked message must NEVER appear in the response HTML.
        """
        self.client.login(username='user1', password='password123')
        response = self.client.get(reverse('message_detail', kwargs={'pk': self.locked_msg.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'messages/locked.html')
        self.assertContains(response, self.locked_msg.title)
        # Verify content is ABSENT
        self.assertNotContains(response, "TOP_SECRET_CONTENT_12345")

    def test_unlocked_message_detail_exposes_content(self):
        self.client.login(username='user1', password='password123')
        response = self.client.get(reverse('message_detail', kwargs={'pk': self.unlocked_msg.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'messages/detail.html')
        self.assertContains(response, self.unlocked_msg.title)
        self.assertContains(response, "REVEALED_MEMORIES_67890")

    def test_user_isolation_cannot_access_other_user_message(self):
        """
        User 2 must not be able to view User 1's messages.
        """
        self.client.login(username='user2', password='password123')

        # Cannot view detail of locked message
        response = self.client.get(reverse('message_detail', kwargs={'pk': self.locked_msg.pk}))
        self.assertEqual(response.status_code, 404)

        # Cannot view detail of unlocked message
        response = self.client.get(reverse('message_detail', kwargs={'pk': self.unlocked_msg.pk}))
        self.assertEqual(response.status_code, 404)

        # Cannot edit
        response = self.client.get(reverse('message_edit', kwargs={'pk': self.locked_msg.pk}))
        self.assertEqual(response.status_code, 404)

        # Cannot delete
        response = self.client.post(reverse('message_delete', kwargs={'pk': self.locked_msg.pk}))
        self.assertEqual(response.status_code, 404)
        # Ensure message was not deleted
        self.assertTrue(Message.objects.filter(pk=self.locked_msg.pk).exists())

    def test_edit_message(self):
        self.client.login(username='user1', password='password123')
        original_unlock_date = self.locked_msg.unlock_date

        response = self.client.post(reverse('message_edit', kwargs={'pk': self.locked_msg.pk}), {
            'title': 'Updated Title',
            'content': 'Updated secret content',
        })
        self.assertRedirects(response, reverse('message_detail', kwargs={'pk': self.locked_msg.pk}))

        self.locked_msg.refresh_from_db()
        self.assertEqual(self.locked_msg.title, 'Updated Title')
        self.assertEqual(self.locked_msg.content, 'Updated secret content')
        # Unlock date remains unmodified
        self.assertEqual(self.locked_msg.unlock_date, original_unlock_date)

    def test_delete_message_post(self):
        self.client.login(username='user1', password='password123')
        response = self.client.post(reverse('message_delete', kwargs={'pk': self.locked_msg.pk}))
        self.assertRedirects(response, reverse('message_list'))
        self.assertFalse(Message.objects.filter(pk=self.locked_msg.pk).exists())

    def test_delete_message_get_does_not_delete(self):
        self.client.login(username='user1', password='password123')
        response = self.client.get(reverse('message_delete', kwargs={'pk': self.locked_msg.pk}))
        self.assertRedirects(response, reverse('message_detail', kwargs={'pk': self.locked_msg.pk}))
        self.assertTrue(Message.objects.filter(pk=self.locked_msg.pk).exists())
