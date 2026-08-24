from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):

    ROLE_CHOICES = [
        ("woman", "Woman"),
        ("family", "Family Member"),
    ]

    STAGE_CHOICES = [
        ("premenopause", "Premenopause"),
        ("perimenopause", "Perimenopause"),
        ("postmenopause", "Postmenopause"),
        ("unknown", "Unknown"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        blank=True,
        null=True
    )

    # Woman's basic information
    age = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    period_status = models.CharField(
        max_length=50,
        blank=True
    )

    period_changes = models.JSONField(
        default=list,
        blank=True
    )

    initial_symptoms = models.JSONField(
        default=list,
        blank=True
    )

    menopause_stage = models.CharField(
        max_length=30,
        choices=STAGE_CHOICES,
        default="unknown"
    )

    onboarding_completed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.username} Profile"


class SymptomEntry(models.Model):

    SYMPTOM_CHOICES = [
        ("hot_flashes", "Hot Flashes"),
        ("night_sweats", "Night Sweats"),
        ("sleep", "Sleep Problems"),
        ("mood", "Mood Changes"),
        ("anxiety", "Anxiety"),
        ("fatigue", "Fatigue"),
        ("headache", "Headache"),
        ("joint_pain", "Joint/Muscle Discomfort"),
        ("brain_fog", "Brain Fog"),
        ("vaginal_dryness", "Vaginal Dryness"),
        ("urinary", "Urinary Changes"),
    ]

    SEVERITY_CHOICES = [
        (1, "Mild"),
        (2, "Moderate"),
        (3, "Severe"),
    ]

    # IMPORTANT:
    # Every symptom now belongs to one specific user.
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="symptoms",
        null=True,
        blank=True
    )

    symptom = models.CharField(
        max_length=50,
        choices=SYMPTOM_CHOICES
    )

    severity = models.IntegerField(
        choices=SEVERITY_CHOICES
    )

    frequency = models.PositiveIntegerField(
        default=1
    )

    date = models.DateField(
        default=timezone.localdate
    )

    notes = models.TextField(
        blank=True
    )

    def __str__(self):
        return (
            f"{self.user.username if self.user else 'No User'} - "
            f"{self.get_symptom_display()} - {self.date}"
        )