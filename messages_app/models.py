from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


CATEGORY_CHOICES = [
    ('personal', 'Personal'),
    ('career', 'Career & Study'),
    ('goals', 'Goals & Aspirations'),
    ('reflections', 'Reflections'),
    ('milestones', 'Milestones & Memories'),
    ('gratitude', 'Gratitude'),
]


class Message(models.Model):
    """
    Represents a message written to the user's future self.
    The message content remains locked until the unlock_date arrives.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    title = models.CharField(
        max_length=200,
        help_text="A short summary or subject for your future self."
    )
    content = models.TextField(
        help_text="The private thoughts or advice to read in the future."
    )
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default='personal',
        blank=True,
        help_text="A category tag for your letter."
    )
    unlock_date = models.DateField(
        help_text="The date when this message will unlock and become readable."
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def is_unlocked(self):
        """
        Check if the unlock date has arrived or passed.
        Comparison is based on the current local date.
        """
        return timezone.localdate() >= self.unlock_date

    def is_locked(self):
        """
        Check if the message is still locked in the future.
        """
        return not self.is_unlocked()

    def days_until_unlock(self):
        """
        Calculate remaining days until the message unlocks.
        Returns 0 if already unlocked.
        """
        today = timezone.localdate()
        if self.unlock_date > today:
            return (self.unlock_date - today).days
        return 0


class Profile(models.Model):
    """
    User profile extension holding additional information such as bio.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text="A brief note about yourself, your vision, or what you are striving for."
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create or save the user profile whenever a User instance is saved.
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        # Ensure profile exists for existing users
        Profile.objects.get_or_create(user=instance)

