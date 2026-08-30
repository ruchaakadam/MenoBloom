from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets


# ============================================================
# USER PROFILE
# ============================================================

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


# ============================================================
# FAMILY CONNECTION
# ============================================================

class FamilyConnection(models.Model):

    woman = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="family_connection"
    )

    family_member = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="connected_woman"
    )

    connection_code = models.CharField(
        max_length=12,
        unique=True,
        blank=True
    )

    share_symptoms = models.BooleanField(
        default=False
    )

    share_nutrition = models.BooleanField(
        default=False
    )

    share_reminders = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        if not self.connection_code:

            while True:

                code = "MB-" + secrets.token_hex(3).upper()

                if not FamilyConnection.objects.filter(
                    connection_code=code
                ).exists():

                    self.connection_code = code
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.woman.username} - "
            f"{self.connection_code}"
        )


# ============================================================
# SYMPTOM ENTRY
# ============================================================

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
            f"{self.get_symptom_display()} - "
            f"{self.date}"
        )


# ============================================================
# HEALTH REMINDER
# ============================================================

class Reminder(models.Model):

    REMINDER_TYPE_CHOICES = [
        ("cancer_screening", "Cancer Screening"),
        ("cervical_screening", "Cervical Cancer Screening"),
        ("bone_health", "Bone Health"),
        ("routine_check", "Routine Health Check"),
        ("medication", "Medication"),
        ("doctor", "Doctor Appointment"),
        ("follow_up", "Follow-up"),
        ("custom", "Custom Reminder"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reminders"
    )

    reminder_type = models.CharField(
        max_length=40,
        choices=REMINDER_TYPE_CHOICES
    )

    title = models.CharField(
        max_length=200
    )

    due_date = models.DateField(
        blank=True,
        null=True
    )

    notes = models.TextField(
        blank=True
    )

    completed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            "completed",
            "due_date",
            "-created_at"
        ]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.title}"
        )

    @property
    def is_overdue(self):

        if not self.due_date:
            return False

        if self.completed:
            return False

        return self.due_date < timezone.localdate()


# ============================================================
# MEAL & NUTRITION TRACKING
# ============================================================

class MealEntry(models.Model):

    MEAL_TYPE_CHOICES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("snack", "Snack"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="meals"
    )

    meal_type = models.CharField(
        max_length=20,
        choices=MEAL_TYPE_CHOICES
    )

    food_name = models.CharField(
        max_length=255
    )

    # Compatibility with existing app
    portion = models.CharField(
        max_length=100,
        blank=True
    )

    quantity = models.CharField(
        max_length=100,
        blank=True
    )

    calories = models.FloatField(
        default=0
    )

    protein = models.FloatField(
        default=0
    )

    calcium = models.FloatField(
        default=0
    )

    carbohydrates = models.FloatField(
        default=0
    )

    fat = models.FloatField(
        default=0
    )

    fiber = models.FloatField(
        default=0
    )

    # IMPORTANT:
    # This is TextField, NOT JSONField.
    # This avoids the SQLite JSON_VALID problem.
    health_benefits = models.TextField(
        blank=True,
        default=""
    )

    menopause_benefit = models.TextField(
        blank=True
    )

    menopause_insight = models.TextField(
        blank=True
    )

    date = models.DateField(
        default=timezone.localdate
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.user.username} - "
            f"{self.food_name} - "
            f"{self.date}"
        )
    # ============================================================
# PRIVATE SECRET NOTE
# ============================================================

class SecretNote(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="secret_notes"
    )

    title = models.CharField(
        max_length=200,
        blank=True
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.title or 'Private Note'}"
        )


# ============================================================
# MENTAL SUPPORT CHAT MESSAGE
# ============================================================

class SupportChatMessage(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="support_chat_messages"
    )

    sender = models.CharField(
        max_length=20,
        choices=[
            ("user", "User"),
            ("bot", "MenoBloom"),
        ]
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.sender}"
        )