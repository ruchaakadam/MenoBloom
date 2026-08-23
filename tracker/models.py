from django.db import models
from django.utils import timezone


class SymptomEntry(models.Model):

    SYMPTOM_CHOICES = [
        ('hot_flashes', 'Hot Flashes'),
        ('night_sweats', 'Night Sweats'),
        ('sleep', 'Sleep Problems'),
        ('mood', 'Mood Changes'),
        ('anxiety', 'Anxiety'),
        ('fatigue', 'Fatigue'),
        ('headache', 'Headache'),
        ('joint_pain', 'Joint/Muscle Discomfort'),
        ('brain_fog', 'Brain Fog'),
        ('vaginal_dryness', 'Vaginal Dryness'),
        ('urinary', 'Urinary Changes'),
    ]

    SEVERITY_CHOICES = [
        (1, 'Mild'),
        (2, 'Moderate'),
        (3, 'Severe'),
    ]

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

    # The date on which the symptom was experienced
    date = models.DateField(
        default=timezone.localdate
    )

    notes = models.TextField(
        blank=True
    )

    def __str__(self):
        return (
            f"{self.get_symptom_display()} "
            f"- {self.date}"
        )