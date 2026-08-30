from django.shortcuts import render, redirect
from django.db.models import Count,Sum
from django.db.models.functions import TruncWeek
from django.utils import timezone
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import SymptomEntry, UserProfile, Reminder, MealEntry, FamilyConnection, SecretNote, SupportChatMessage

# ============================================================
# HELPER
# ============================================================

def get_profile(user):
    """
    Get the user's profile.
    Create it automatically if it doesn't exist.
    """

    profile, created = UserProfile.objects.get_or_create(
        user=user
    )

    return profile


# ============================================================
# HOME
# ============================================================

def home(request):

    if request.user.is_authenticated:

        profile = get_profile(request.user)

        if profile.onboarding_completed:

            if profile.role == "family":
                return redirect("family")

            return redirect("dashboard")

        return redirect("choose_role")

    return redirect("login")


# ============================================================
# DASHBOARD
# ============================================================

@login_required(login_url="/login/")
def dashboard(request):

    profile = get_profile(request.user)

    if not profile.onboarding_completed:
        return redirect("choose_role")

    symptoms = SymptomEntry.objects.filter(
        user=request.user
    ).order_by("-date", "-id")

    total_symptoms = symptoms.count()
    recent_symptoms = symptoms[:5]

    pending_reminders = Reminder.objects.filter(
        user=request.user,
        completed=False
    ).order_by("due_date", "-created_at")

    health_reminders = pending_reminders.count()

    today = timezone.localdate()

    today_meals = MealEntry.objects.filter(
        user=request.user,
        date=today
    ).order_by("-created_at")

    daily_totals = today_meals.aggregate(
        calories=Sum("calories"),
        protein=Sum("protein"),
        calcium=Sum("calcium"),
        carbohydrates=Sum("carbohydrates"),
        fat=Sum("fat"),
        fiber=Sum("fiber")
    )

    calories = daily_totals["calories"] or 0
    protein = daily_totals["protein"] or 0
    calcium = daily_totals["calcium"] or 0
    carbohydrates = daily_totals["carbohydrates"] or 0
    fat = daily_totals["fat"] or 0
    fiber = daily_totals["fiber"] or 0

    # --------------------------------------------------------
    # WELLNESS TRACKING SCORE
    # This measures app engagement, not medical health.
    # --------------------------------------------------------

    if total_symptoms >= 5:
        symptom_score = 30
    elif total_symptoms >= 3:
        symptom_score = 22
    elif total_symptoms >= 1:
        symptom_score = 15
    else:
        symptom_score = 0

    if today_meals.count() >= 3:
        nutrition_score = 30
    elif today_meals.count() == 2:
        nutrition_score = 22
    elif today_meals.count() == 1:
        nutrition_score = 15
    else:
        nutrition_score = 0

    if health_reminders == 0:
        reminder_score = 20
    elif health_reminders <= 2:
        reminder_score = 15
    elif health_reminders <= 4:
        reminder_score = 10
    else:
        reminder_score = 5

    if total_symptoms > 0 and today_meals.exists():
        engagement_score = 20
    elif total_symptoms > 0 or today_meals.exists():
        engagement_score = 12
    else:
        engagement_score = 0

    tracking_score = (
        symptom_score
        + nutrition_score
        + reminder_score
        + engagement_score
    )

    if tracking_score >= 80:
        tracking_status = "Great Tracking"
        tracking_message = (
            "You're keeping up well with your wellness tracking."
        )
    elif tracking_score >= 60:
        tracking_status = "On Track"
        tracking_message = (
            "You're building a consistent wellness tracking routine."
        )
    elif tracking_score >= 30:
        tracking_status = "Getting Started"
        tracking_message = (
            "Keep logging symptoms and meals to build a useful history."
        )
    else:
        tracking_status = "Let's Get Started"
        tracking_message = (
            "Start by recording a symptom or logging your first meal."
        )

    symptom_progress = round((symptom_score / 30) * 100)
    nutrition_progress = round((nutrition_score / 30) * 100)
    reminder_progress = round((reminder_score / 20) * 100)
    engagement_progress = round((engagement_score / 20) * 100)

    stage_names = {
        "premenopause": "Premenopause",
        "perimenopause": "Perimenopause",
        "postmenopause": "Postmenopause",
        "unknown": "Not Yet Estimated"
    }

    menopause_stage = stage_names.get(
        profile.menopause_stage,
        "Not Yet Estimated"
    )

    context = {
        "profile": profile,
        "menopause_stage": menopause_stage,
        "symptoms": symptoms,
        "recent_symptoms": recent_symptoms,
        "total_symptoms": total_symptoms,
        "pending_reminders": pending_reminders,
        "health_reminders": health_reminders,
        "today_meals": today_meals,
        "meal_count": today_meals.count(),
        "calories": round(calories, 1),
        "protein": round(protein, 1),
        "calcium": round(calcium, 1),
        "carbohydrates": round(carbohydrates, 1),
        "fat": round(fat, 1),
        "fiber": round(fiber, 1),
        "tracking_score": tracking_score,
        "tracking_status": tracking_status,
        "tracking_message": tracking_message,
        "symptom_progress": symptom_progress,
        "nutrition_progress": nutrition_progress,
        "reminder_progress": reminder_progress,
        "engagement_progress": engagement_progress,
        "today": today,
    }

    return render(
        request,
        "tracker/dashboard.html",
        context
    )


# ============================================================
# ADD / RECORD SYMPTOM
# ============================================================

@login_required(login_url="/login/")
def add_symptom(request):

    profile = get_profile(request.user)

    if not profile.onboarding_completed:

        return redirect("woman_onboarding")

    if request.method == "POST":

        selected_symptoms = request.POST.getlist(
            "symptoms"
        )

        date = request.POST.get("date")

        notes = request.POST.get(
            "notes",
            ""
        )

        for symptom in selected_symptoms:

            severity = request.POST.get(
                f"severity_{symptom}",
                "1"
            )

            frequency = request.POST.get(
                f"frequency_{symptom}",
                1
            )

            try:

                severity = int(severity)

            except (
                ValueError,
                TypeError
            ):

                severity = 1

            try:

                frequency = int(frequency)

            except (
                ValueError,
                TypeError
            ):

                frequency = 1

            SymptomEntry.objects.create(

                user=request.user,

                symptom=symptom,

                severity=severity,

                frequency=frequency,

                date=date if date else None,

                notes=notes
            )

        return redirect("dashboard")

    return render(
        request,
        "tracker/add_symptom.html"
    )

def analysis(request):

    # ============================================================
    # LOGIN CHECK
    # ============================================================

    if not request.user.is_authenticated:
        return redirect("login")


    # ============================================================
    # GET ALL SYMPTOMS FOR CURRENT USER
    # ============================================================

    symptoms = SymptomEntry.objects.filter(
        user=request.user
    ).order_by(
        "-date",
        "-id"
    )


    # ============================================================
    # WEEKLY DATA FOR GRAPH
    # ============================================================

    weekly_data = []


    for entry in symptoms:

        weekly_data.append({

            "week": entry.date.strftime("%Y-%m-%d"),

            "symptom": entry.symptom,

            "frequency": entry.frequency,

        })


    # ============================================================
    # CONTEXT
    # ============================================================

    context = {

        "symptoms": symptoms,

        "weekly_data": json.dumps(
            weekly_data
        ),

    }


    # ============================================================
    # RENDER
    # ============================================================

    return render(
        request,
        "tracker/analysis.html",
        context
    )
# ============================================================
# HEALTH REMINDERS
# ============================================================

@login_required(login_url="/login/")
def reminders(request):

    pending_reminders = Reminder.objects.filter(
        user=request.user,
        completed=False
    ).order_by(
        "due_date"
    )

    completed_reminders = Reminder.objects.filter(
        user=request.user,
        completed=True
    ).order_by(
        "-updated_at"
    )

    return render(
        request,
        "tracker/reminders.html",
        {
            "pending_reminders":
                pending_reminders,

            "completed_reminders":
                completed_reminders,
        }
    )


# ============================================================
# ADD REMINDER
# ============================================================

@login_required(login_url="/login/")
def add_reminder(request):

    if request.method != "POST":

        return redirect(
            "reminders"
        )

    reminder_type = request.POST.get(
        "reminder_type",
        "custom"
    )

    title = request.POST.get(
        "title",
        ""
    ).strip()

    due_date = request.POST.get(
        "due_date",
        ""
    )

    notes = request.POST.get(
        "notes",
        ""
    ).strip()

    # Don't create empty reminders
    if not title:

        return redirect(
            "reminders"
        )

    valid_types = [
        choice[0]
        for choice
        in Reminder.REMINDER_TYPE_CHOICES
    ]

    if reminder_type not in valid_types:

        reminder_type = "custom"

    Reminder.objects.create(

        user=request.user,

        reminder_type=reminder_type,

        title=title,

        due_date=(
            due_date
            if due_date
            else None
        ),

        notes=notes

    )

    return redirect(
        "reminders"
    )


# ============================================================
# COMPLETE REMINDER
# ============================================================

@login_required(login_url="/login/")
def complete_reminder(
    request,
    reminder_id
):

    if request.method != "POST":

        return redirect(
            "reminders"
        )

    reminder = Reminder.objects.filter(

        id=reminder_id,

        user=request.user

    ).first()

    if reminder:

        reminder.completed = True

        reminder.save()

    return redirect(
        "reminders"
    )


# ============================================================
# DELETE REMINDER
# ============================================================

@login_required(login_url="/login/")
def delete_reminder(
    request,
    reminder_id
):

    if request.method != "POST":

        return redirect(
            "reminders"
        )

    reminder = Reminder.objects.filter(

        id=reminder_id,

        user=request.user

    ).first()

    if reminder:

        reminder.delete()

    return redirect(
        "reminders"
    )

# ============================================================
# FOOD & LIFESTYLE
# ============================================================
# ============================================================
# FOOD & NUTRITION
# ============================================================

@login_required(login_url="/login/")
def food(request):

    today = timezone.localdate()

    # --------------------------------------------------------
    # CURATED FOOD DATABASE
    #
    # Values are approximate per listed serving.
    # These are intentionally presented as estimates because
    # preparation and portion sizes can change nutrition values.
    # --------------------------------------------------------

    food_database = {

        "egg": {
            "name": "Egg",
            "calories": 78,
            "protein": 6.3,
            "calcium": 25,
            "carbohydrates": 0.6,
            "fat": 5.3,
            "fiber": 0,
            "benefits": [
                "Provides high-quality protein.",
                "Contains nutrients that support overall wellness.",
                "Can be part of a balanced breakfast or meal."
            ],
            "insight":
                "Eggs provide protein, which can be useful "
                "for maintaining muscle during midlife."
        },

        "milk": {
            "name": "Milk",
            "calories": 122,
            "protein": 8.0,
            "calcium": 300,
            "carbohydrates": 12,
            "fat": 5.0,
            "fiber": 0,
            "benefits": [
                "Good source of calcium.",
                "Provides protein.",
                "Can contribute to daily bone-health nutrition."
            ],
            "insight":
                "Milk can contribute calcium and protein to the diet, "
                "nutrients that are useful to pay attention to during "
                "midlife."
        },

        "curd": {
            "name": "Curd / Yogurt",
            "calories": 100,
            "protein": 5.0,
            "calcium": 150,
            "carbohydrates": 7.0,
            "fat": 5.0,
            "fiber": 0,
            "benefits": [
                "Provides calcium.",
                "Provides protein.",
                "Can be included as part of a balanced meal."
            ],
            "insight":
                "Curd can contribute calcium and protein while making "
                "a convenient addition to meals or snacks."
        },

        "paneer": {
            "name": "Paneer",
            "calories": 265,
            "protein": 18.0,
            "calcium": 208,
            "carbohydrates": 6.0,
            "fat": 20.0,
            "fiber": 0,
            "benefits": [
                "Rich in protein.",
                "Provides calcium.",
                "Can support a protein-rich meal."
            ],
            "insight":
                "Paneer can provide both protein and calcium, making "
                "it useful in a balanced midlife diet."
        },

        "tofu": {
            "name": "Tofu",
            "calories": 144,
            "protein": 17.0,
            "calcium": 350,
            "carbohydrates": 3.0,
            "fat": 9.0,
            "fiber": 2.0,
            "benefits": [
                "Plant-based source of protein.",
                "Some varieties provide substantial calcium.",
                "Can be used in many balanced meals."
            ],
            "insight":
                "Tofu can be a useful plant-based source of protein "
                "and, depending on preparation, calcium."
        },

        "spinach": {
            "name": "Spinach",
            "calories": 23,
            "protein": 2.9,
            "calcium": 99,
            "carbohydrates": 3.6,
            "fat": 0.4,
            "fiber": 2.2,
            "benefits": [
                "Provides dietary fiber.",
                "Contains several vitamins and minerals.",
                "Adds vegetables to the meal."
            ],
            "insight":
                "Adding leafy vegetables such as spinach can help "
                "increase vegetable and fiber intake."
        },

        "dal": {
            "name": "Dal",
            "calories": 180,
            "protein": 9.0,
            "calcium": 40,
            "carbohydrates": 30,
            "fat": 3.0,
            "fiber": 8.0,
            "benefits": [
                "Provides plant-based protein.",
                "Good source of dietary fiber.",
                "Can contribute to a balanced meal."
            ],
            "insight":
                "Dal can help add plant-based protein and fiber "
                "to everyday meals."
        },

        "chickpeas": {
            "name": "Chickpeas",
            "calories": 269,
            "protein": 14.5,
            "calcium": 49,
            "carbohydrates": 45,
            "fat": 4.2,
            "fiber": 12.5,
            "benefits": [
                "Good source of plant-based protein.",
                "High in dietary fiber.",
                "Can support a filling balanced meal."
            ],
            "insight":
                "Chickpeas provide protein and fiber and can be "
                "a useful component of a balanced diet."
        },

        "almonds": {
            "name": "Almonds",
            "calories": 164,
            "protein": 6.0,
            "calcium": 76,
            "carbohydrates": 6.1,
            "fat": 14.2,
            "fiber": 3.5,
            "benefits": [
                "Provides protein and healthy fats.",
                "Contains calcium.",
                "Provides dietary fiber."
            ],
            "insight":
                "Nuts such as almonds can add protein, healthy fats "
                "and some calcium to meals or snacks."
        },

        "oats": {
            "name": "Oats",
            "calories": 150,
            "protein": 5.0,
            "calcium": 20,
            "carbohydrates": 27,
            "fat": 3.0,
            "fiber": 4.0,
            "benefits": [
                "Provides dietary fiber.",
                "Provides some plant-based protein.",
                "Can form a balanced breakfast base."
            ],
            "insight":
                "Oats can contribute fiber and make a useful base "
                "for a balanced breakfast."
        },

        "banana": {
            "name": "Banana",
            "calories": 105,
            "protein": 1.3,
            "calcium": 6,
            "carbohydrates": 27,
            "fat": 0.4,
            "fiber": 3.1,
            "benefits": [
                "Provides dietary fiber.",
                "Provides carbohydrates for energy.",
                "Convenient fruit option."
            ],
            "insight":
                "Fruit can help add fiber and micronutrients to "
                "the overall diet."
        },

        "apple": {
            "name": "Apple",
            "calories": 95,
            "protein": 0.5,
            "calcium": 11,
            "carbohydrates": 25,
            "fat": 0.3,
            "fiber": 4.4,
            "benefits": [
                "Provides dietary fiber.",
                "Adds fruit to the diet.",
                "Convenient snack option."
            ],
            "insight":
                "Whole fruit can contribute dietary fiber and "
                "variety to a balanced eating pattern."
        },

        "roti": {
            "name": "Roti",
            "calories": 120,
            "protein": 3.5,
            "calcium": 15,
            "carbohydrates": 22,
            "fat": 2.5,
            "fiber": 3.0,
            "benefits": [
                "Provides carbohydrates for energy.",
                "Can contribute dietary fiber depending on flour used.",
                "Works well as part of a balanced meal."
            ],
            "insight":
                "Pairing roti with vegetables and a protein source "
                "can make a more balanced meal."
        },

        "rice": {
            "name": "Cooked Rice",
            "calories": 205,
            "protein": 4.3,
            "calcium": 16,
            "carbohydrates": 44.5,
            "fat": 0.4,
            "fiber": 0.6,
            "benefits": [
                "Provides carbohydrates for energy.",
                "Can form part of a balanced meal.",
                "Pairs well with protein and vegetables."
            ],
            "insight":
                "Combining rice with protein and vegetables can "
                "create a more balanced meal."
        },

        "chicken": {
            "name": "Chicken",
            "calories": 231,
            "protein": 43.5,
            "calcium": 15,
            "carbohydrates": 0,
            "fat": 5.0,
            "fiber": 0,
            "benefits": [
                "High in protein.",
                "Can support muscle maintenance.",
                "Works well with vegetables and whole grains."
            ],
            "insight":
                "Protein-rich foods can be useful for supporting "
                "muscle maintenance during midlife."
        },

        "fish": {
            "name": "Fish",
            "calories": 206,
            "protein": 22.0,
            "calcium": 20,
            "carbohydrates": 0,
            "fat": 12.0,
            "fiber": 0,
            "benefits": [
                "Provides protein.",
                "Many fish varieties provide omega-3 fats.",
                "Can form part of a balanced meal."
            ],
            "insight":
                "Fish can contribute protein, and some varieties "
                "also provide omega-3 fatty acids."
        },

    }


    # --------------------------------------------------------
    # MEAL ANALYSIS
    # --------------------------------------------------------

    analysis = None

    error = None


    if request.method == "POST":

        food_name = request.POST.get(
            "food_name",
            ""
        ).strip().lower()

        meal_type = request.POST.get(
            "meal_type",
            "breakfast"
        )

        portion = request.POST.get(
            "portion",
            ""
        ).strip()


        if not food_name:

            error = (
                "Please enter a food before "
                "analyzing your meal."
            )

        else:

            # ------------------------------------------------
            # Find food
            # ------------------------------------------------

            food_key = None


            for key in food_database:

                if (
                    key in food_name
                    or
                    food_name in key
                ):

                    food_key = key

                    break


            if food_key is None:

                error = (
                    "We don't have this food in our "
                    "current nutrition database yet. "
                    "Try a common food such as egg, "
                    "milk, paneer, dal, roti, rice, "
                    "spinach, oats or almonds."
                )

            else:

                food = food_database[food_key]


                # --------------------------------------------
                # Create analysis
                # --------------------------------------------

                analysis = {

                    "name":
                        food["name"],

                    "calories":
                        food["calories"],

                    "protein":
                        food["protein"],

                    "calcium":
                        food["calcium"],

                    "carbohydrates":
                        food["carbohydrates"],

                    "fat":
                        food["fat"],

                    "fiber":
                        food["fiber"],

                    "benefits":
                        food["benefits"],

                    "insight":
                        food["insight"],

                    "meal_type":
                        meal_type,

                    "portion":
                        portion

                }


                # --------------------------------------------
                # Save to database
                # --------------------------------------------

                MealEntry.objects.create(

                    user=request.user,

                    meal_type=meal_type,

                    food_name=food["name"],

                    portion=portion,

                    calories=food["calories"],

                    protein=food["protein"],

                    calcium=food["calcium"],

                    carbohydrates=
                        food["carbohydrates"],

                    fat=
                        food["fat"],

                    fiber=
                        food["fiber"],

                    health_benefits=
                        "\n".join(food["benefits"]),

                    menopause_insight=
                        food["insight"],

                    date=today

                )


    # --------------------------------------------------------
    # TODAY'S MEALS
    # --------------------------------------------------------

    today_meals = MealEntry.objects.filter(

        user=request.user,

        date=today

    ).order_by(
        "-created_at"
    )


    # --------------------------------------------------------
    # DAILY TOTALS
    # --------------------------------------------------------

    daily_totals = today_meals.aggregate(

        calories=Sum(
            "calories"
        ),

        protein=Sum(
            "protein"
        ),

        calcium=Sum(
            "calcium"
        ),

        carbohydrates=Sum(
            "carbohydrates"
        ),

        fat=Sum(
            "fat"
        ),

        fiber=Sum(
            "fiber"
        )

    )


    context = {

        "analysis":
            analysis,

        "error":
            error,

        "today_meals":
            today_meals,

        "daily_totals":
            daily_totals,

        "food_options":
            food_database.keys()

    }


    return render(

        request,

        "tracker/food.html",

        context

    )
# ============================================================
# LOGIN
# ============================================================

def login_view(request):

    # Already logged in
    if request.user.is_authenticated:

        profile = get_profile(request.user)

        if profile.onboarding_completed:

            if profile.role == "family":

                return redirect("family")

            return redirect("dashboard")

        return redirect("choose_role")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            profile = get_profile(user)

            # Existing completed users go directly
            # to their own dashboard.
            if profile.onboarding_completed:

                if profile.role == "family":

                    return redirect(
                        "family"
                    )

                return redirect(
                    "dashboard"
                )

            # New/incomplete user
            return redirect(
                "choose_role"
            )

        return render(

            request,

            "tracker/login.html",

            {
                "error":
                    "Invalid username or password."
            }
        )

    return render(
        request,
        "tracker/login.html"
    )


# ============================================================
# SIGNUP
# ============================================================

def signup(request):

    if request.user.is_authenticated:

        return redirect(
            "home"
        )

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        # Password confirmation
        if password != confirm_password:

            return render(

                request,

                "tracker/signup.html",

                {
                    "error":
                        "Passwords do not match."
                }
            )

        # Username check
        if User.objects.filter(
            username=username
        ).exists():

            return render(

                request,

                "tracker/signup.html",

                {
                    "error":
                        "Username already exists."
                }
            )

        # Create Django user
        #
        # IMPORTANT:
        # Django stores a HASHED password.
        # We do NOT store the raw password.

        user = User.objects.create_user(

            username=username,

            email=email,

            password=password
        )

        # Create empty profile
        UserProfile.objects.create(
            user=user
        )

        # Login immediately
        login(
            request,
            user
        )

        return redirect(
            "choose_role"
        )

    return render(
        request,
        "tracker/signup.html"
    )


# ============================================================
# CHOOSE ROLE
# ============================================================

@login_required(login_url="/login/")
def choose_role(request):

    profile = get_profile(request.user)

    # If role/onboarding is already completed,
    # DON'T show this page again.
    if profile.onboarding_completed:

        if profile.role == "family":

            return redirect(
                "family"
            )

        return redirect(
            "dashboard"
        )

    return render(
        request,
        "tracker/choose_role.html"
    )


# ============================================================
# SET ROLE
# ============================================================

@login_required(login_url="/login/")
def set_role(request, role):

    profile = get_profile(request.user)

    # If already completed, don't repeat setup
    if profile.onboarding_completed:

        if profile.role == "family":

            return redirect(
                "family"
            )

        return redirect(
            "dashboard"
        )

    if role not in [
        "woman",
        "family"
    ]:

        return redirect(
            "choose_role"
        )

    profile.role = role

    profile.save()

    # Woman needs personal details
    if role == "woman":

        return redirect(
            "woman_onboarding"
        )

    # Family member doesn't need
    # woman's health onboarding
    profile.onboarding_completed = True

    profile.save()

    return redirect(
        "family"
    )


# ============================================================
# WOMAN ONBOARDING / DETAILS
# ============================================================

@login_required(login_url="/login/")
def woman_onboarding(request):

    profile = get_profile(request.user)

    # Already completed
    if profile.onboarding_completed:

        return redirect(
            "dashboard"
        )

    # Only women should access this
    if profile.role != "woman":

        return redirect(
            "choose_role"
        )

    if request.method == "POST":

        # =====================================================
        # GET USER INFORMATION
        # =====================================================

        age = request.POST.get(
            "age"
        )

        period_status = request.POST.get(
            "period_status"
        )

        period_changes = request.POST.getlist(
            "period_changes"
        )

        symptoms = request.POST.getlist(
            "symptoms"
        )


        # =====================================================
        # STAGE ESTIMATION
        # =====================================================

        reasons = []

        if period_status == "12_months":

            stage = "Postmenopause"

            stage_description = (
                "Your responses indicate that you "
                "have not had a menstrual period "
                "for 12 months or more. This pattern "
                "is consistent with menopause having "
                "been reached."
            )

            reasons.append(
                "No period reported for 12 months or more."
            )

        elif period_status == "months_missing":

            stage = "Late Perimenopause"

            stage_description = (
                "Your responses suggest that you may "
                "be in the later part of the menopausal "
                "transition, particularly because you "
                "are experiencing skipped periods."
            )

            reasons.append(
                "You reported skipping periods."
            )

        elif period_status == "irregular":

            stage = "Perimenopause"

            stage_description = (
                "Your responses suggest that you may "
                "be experiencing the menopausal "
                "transition, particularly because "
                "your menstrual pattern has become "
                "irregular."
            )

            reasons.append(
                "Your periods have become irregular."
            )

        elif period_status == "regular":

            stage = "Premenopause"

            stage_description = (
                "Your reported menstrual pattern is "
                "still regular. Based on this information "
                "alone, your pattern does not currently "
                "suggest that you have reached menopause."
            )

            reasons.append(
                "You reported that your periods are still regular."
            )

        else:

            stage = "Unable to estimate"

            stage_description = (
                "There isn't enough information to "
                "provide an educational estimate yet."
            )


        # =====================================================
        # ADDITIONAL REASONS
        # =====================================================

        if "cycle_length" in period_changes:

            reasons.append(
                "You reported changes in cycle length."
            )

        if "skipped" in period_changes:

            reasons.append(
                "You reported skipped periods."
            )

        if len(symptoms) > 0:

            reasons.append(
                f"You reported {len(symptoms)} "
                f"menopause-related symptom(s)."
            )


        # =====================================================
        # SAVE PROFILE
        # =====================================================

        profile.age = age

        profile.period_status = (
            period_status
        )

        profile.period_changes = (
            period_changes
        )

        profile.initial_symptoms = (
            symptoms
        )

        profile.menopause_stage = (
            stage.lower()
            .replace(
                " ",
                "_"
            )
        )

        profile.onboarding_completed = True

        profile.save()


        # =====================================================
        # RESULT PAGE
        # =====================================================

        period_names = {

            "regular":
                "Regular",

            "irregular":
                "Irregular",

            "months_missing":
                "Occasionally skipped",

            "12_months":
                "No period for 12+ months",
        }


        return render(

            request,

            "tracker/stage_result.html",

            {

                "stage":
                    stage,

                "stage_description":
                    stage_description,

                "reasons":
                    reasons,

                "profile":
                    profile,

                "period_status_display":
                    period_names.get(
                        period_status,
                        "Not specified"
                    ),

                "symptom_count":
                    len(symptoms),
            }
        )


    # =========================================================
    # FIRST TIME WOMAN ONBOARDING PAGE
    # =========================================================

    return render(

        request,

        "tracker/woman_onboarding.html",

        {
            "profile": profile
        }
    )
# ============================================================
# FAMILY MEMBER DASHBOARD
# ============================================================

@login_required(login_url="/login/")
def family(request):

    profile = get_profile(request.user)

    # Family accounts only
    if profile.role != "family":
        return redirect("dashboard")

    error = None
    success = None

    # ========================================================
    # CONNECT ACCOUNT
    # ========================================================

    if request.method == "POST":

        code = request.POST.get(
            "connection_code",
            ""
        ).strip().upper()

        if not code:

            error = "Please enter a connection code."

        else:

            try:

                connection = FamilyConnection.objects.get(
                    connection_code=code
                )

                # Cannot connect to yourself
                if connection.woman == request.user:

                    error = (
                        "You cannot connect your account "
                        "to itself."
                    )

                # Code already belongs to another family member
                elif (
                    connection.family_member
                    and
                    connection.family_member != request.user
                ):

                    error = (
                        "This connection code is already "
                        "connected to another family member."
                    )

                else:

                    connection.family_member = request.user
                    connection.save()

                    success = (
                        "Account connected successfully."
                    )

            except FamilyConnection.DoesNotExist:

                error = (
                    "That connection code is not valid."
                )

    # ========================================================
    # GET CURRENT CONNECTION
    # ========================================================

    connection = (
        FamilyConnection.objects
        .filter(
            family_member=request.user
        )
        .select_related("woman")
        .first()
    )

    connected_woman = None

    if connection:

        connected_woman = connection.woman

    # ========================================================
    # SHARED DATA
    # ========================================================

    shared_symptoms = []
    shared_meals = []
    shared_reminders = []

    # ========================================================
    # ONLY LOAD DATA IF CONNECTED
    # ========================================================

    if connection and connected_woman:

        # ----------------------------------------------------
        # SYMPTOMS
        # ----------------------------------------------------

        if connection.share_symptoms:

            shared_symptoms = list(
                SymptomEntry.objects
                .filter(
                    user=connected_woman
                )
                .order_by(
                    "-date",
                    "-id"
                )[:10]
            )

        # ----------------------------------------------------
        # NUTRITION
        # ----------------------------------------------------

        if connection.share_nutrition:

            shared_meals = list(
                MealEntry.objects
                .filter(
                    user=connected_woman
                )
                .order_by(
                    "-date",
                    "-created_at"
                )[:10]
            )

        # ----------------------------------------------------
        # REMINDERS
        # ----------------------------------------------------

        if connection.share_reminders:

            shared_reminders = list(
                Reminder.objects
                .filter(
                    user=connected_woman
                )
                .order_by(
                    "completed",
                    "due_date"
                )[:10]
            )

    # ========================================================
    # FAMILY MEMBER'S OWN REMINDERS
    # ========================================================

    own_reminders = (
        Reminder.objects
        .filter(
            user=request.user
        )
        .order_by(
            "completed",
            "due_date"
        )
    )

    pending_reminders = own_reminders.filter(
        completed=False
    )

    completed_reminders = own_reminders.filter(
        completed=True
    )

    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "tracker/family.html",
        {
            "profile":
                profile,

            "connection":
                connection,

            "linked_woman":
                connected_woman,

            "shared_symptoms":
                shared_symptoms,

            "shared_meals":
                shared_meals,

            "shared_reminders":
                shared_reminders,

            "pending_reminders":
                pending_reminders,

            "completed_reminders":
                completed_reminders,

            "error":
                error,

            "success":
                success,
        }
    )
# ============================================================
# DISCONNECT FAMILY ACCOUNT
# ============================================================

@login_required(login_url="/login/")
def disconnect_family(request):

    if request.method != "POST":
        return redirect("family")

    connection = (
        FamilyConnection.objects
        .filter(
            family_member=request.user
        )
        .first()
    )

    if connection:
        connection.family_member = None
        connection.save()

    return redirect("family")
# ============================================================
# LOGOUT
# ============================================================

def logout_view(request):

    logout(request)

    return redirect(
        "login"
    )


# ============================================================
# MENOPAUSE INFORMATION
# ============================================================

def menopause_info(request):

    return render(

        request,

        "tracker/menopause_info.html"
    )
# ============================================================
# GYNECOLOGIST FINDER
# ============================================================

@login_required(login_url="/login/")
def gynecologist(request):

    return render(
        request,
        "tracker/gynecologist.html"
    )


def logout_view(request):
    logout(request)
    return redirect("login")

# ============================================================
# PROFILE
# ============================================================

@login_required(login_url="/login/")
def profile_view(request):

    profile = get_profile(request.user)

    # ========================================================
    # WOMAN'S FAMILY CONNECTION
    # ========================================================

    family_connection = None

    if profile.role == "woman":

        family_connection, created = (
            FamilyConnection.objects.get_or_create(
                woman=request.user
            )
        )

    # ========================================================
    # UPDATE PROFILE
    # ========================================================

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        # ----------------------------------------------------
        # USERNAME
        # ----------------------------------------------------

        if not username:

            return render(
                request,
                "tracker/profile.html",
                {
                    "profile": profile,
                    "family_connection":
                        family_connection,
                    "error":
                        "Username cannot be empty."
                }
            )

        if User.objects.filter(
            username=username
        ).exclude(
            id=request.user.id
        ).exists():

            return render(
                request,
                "tracker/profile.html",
                {
                    "profile": profile,
                    "family_connection":
                        family_connection,
                    "error":
                        "Username already exists."
                }
            )

        # ----------------------------------------------------
        # UPDATE USER
        # ----------------------------------------------------

        request.user.username = username
        request.user.email = email
        request.user.save()

        # ----------------------------------------------------
        # AGE
        # ----------------------------------------------------

        age = request.POST.get(
            "age",
            ""
        ).strip()

        if age:

            try:
                profile.age = int(age)

            except ValueError:

                return render(
                    request,
                    "tracker/profile.html",
                    {
                        "profile": profile,
                        "family_connection":
                            family_connection,
                        "error":
                            "Please enter a valid age."
                    }
                )

        # ----------------------------------------------------
        # FAMILY SHARING
        # ----------------------------------------------------

        if (
            profile.role == "woman"
            and family_connection
        ):

            family_connection.share_symptoms = (
                request.POST.get(
                    "share_symptoms"
                ) == "on"
            )

            family_connection.share_nutrition = (
                request.POST.get(
                    "share_nutrition"
                ) == "on"
            )

            family_connection.share_reminders = (
                request.POST.get(
                    "share_reminders"
                ) == "on"
            )

            family_connection.save()

        # ----------------------------------------------------
        # SAVE PROFILE
        # ----------------------------------------------------

        profile.save()

        return redirect("profile")

    # ========================================================
    # DISPLAY VALUES
    # ========================================================

    stage_names = {

        "premenopause":
            "Premenopause",

        "perimenopause":
            "Perimenopause",

        "postmenopause":
            "Postmenopause",

        "unknown":
            "Not Yet Estimated",

        "unable_to_estimate":
            "Not Yet Estimated",
    }

    period_names = {

        "regular":
            "Regular",

        "irregular":
            "Irregular",

        "months_missing":
            "Occasionally skipped",

        "12_months":
            "No period for 12+ months",
    }

    # ========================================================
    # CONNECTED FAMILY MEMBER
    # ========================================================

    connected_family_member = None

    if family_connection:

        connected_family_member = (
            family_connection.family_member
        )

    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        "profile":
            profile,

        "username":
            request.user.username,

        "email":
            request.user.email,

        "menopause_stage":
            stage_names.get(
                profile.menopause_stage,
                "Not Yet Estimated"
            ),

        "period_status":
            period_names.get(
                profile.period_status,
                "Not specified"
            ),

        "role":
            (
                "Woman"
                if profile.role == "woman"
                else "Family Member"
            ),

        "family_connection":
            family_connection,

        "connected_family_member":
            connected_family_member,
    }

    return render(
        request,
        "tracker/profile.html",
        context
    )
# ============================================================
# MENTAL SUPPORT CHAT
# ============================================================

@login_required(login_url="/login/")
def mental_support(request):

    messages = SupportChatMessage.objects.filter(
        user=request.user
    )

    if request.method == "POST":

        user_message = request.POST.get(
            "message",
            ""
        ).strip()

        if user_message:

            SupportChatMessage.objects.create(
                user=request.user,
                sender="user",
                message=user_message
            )

            text = user_message.lower()

            # ------------------------------------------------
            # SUPPORTIVE RESPONSES
            # ------------------------------------------------

            if any(
                word in text
                for word in [
                    "suicide",
                    "kill myself",
                    "end my life",
                    "want to die",
                    "self harm",
                    "hurt myself"
                ]
            ):

                response = (
                    "I'm really sorry you're going through "
                    "something this difficult. You don't have "
                    "to handle it alone. Please contact a "
                    "trusted person or a qualified mental-health "
                    "professional right now. If you are in "
                    "immediate danger, contact your local "
                    "emergency service."
                )

            elif any(
                word in text
                for word in [
                    "anxious",
                    "anxiety",
                    "panic",
                    "worried",
                    "stress"
                ]
            ):

                response = (
                    "It sounds like you're carrying a lot right "
                    "now. Try taking a slow breath and giving "
                    "yourself a quiet moment. You don't have to "
                    "solve everything at once. If these feelings "
                    "keep interfering with your daily life, "
                    "consider talking with a healthcare or "
                    "mental-health professional."
                )

            elif any(
                word in text
                for word in [
                    "sad",
                    "sadness",
                    "cry",
                    "crying",
                    "lonely",
                    "alone"
                ]
            ):

                response = (
                    "I'm glad you put those feelings into words. "
                    "It's okay to have difficult days. Consider "
                    "reaching out to someone you trust and giving "
                    "yourself some time and space to rest."
                )

            elif any(
                word in text
                for word in [
                    "sleep",
                    "insomnia",
                    "can't sleep",
                    "cannot sleep"
                ]
            ):

                response = (
                    "Sleep difficulties can feel exhausting. "
                    "A calming routine, reducing screen time "
                    "before bed, and keeping a consistent sleep "
                    "schedule may help. If sleep problems continue, "
                    "consider discussing them with your doctor."
                )

            elif any(
                word in text
                for word in [
                    "angry",
                    "irritated",
                    "irritation",
                    "mood"
                ]
            ):

                response = (
                    "Changes in mood can feel frustrating. "
                    "You could try stepping away for a few minutes, "
                    "taking some slow breaths, or writing down "
                    "what you're feeling. You deserve a space where "
                    "you can express those feelings without judgment."
                )

            elif any(
                word in text
                for word in [
                    "help",
                    "support",
                    "feel",
                    "feeling"
                ]
            ):

                response = (
                    "I'm here to listen. You can tell me what "
                    "has been bothering you, how you're feeling, "
                    "or simply write down what's on your mind. "
                    "You don't need to phrase it perfectly."
                )

            else:

                response = (
                    "Thank you for sharing that with me. "
                    "Take your time. What you're feeling is worth "
                    "paying attention to. If you'd like, tell me "
                    "a little more about what's been on your mind."
                )

            SupportChatMessage.objects.create(
                user=request.user,
                sender="bot",
                message=response
            )

            return redirect("mental_support")

    return render(
        request,
        "tracker/mental_support.html",
        {
            "messages": messages
        }
    )
# ============================================================
# SECRET NOTES
# ============================================================

@login_required(login_url="/login/")
def secret_notes(request):

    notes = SecretNote.objects.filter(
        user=request.user
    )

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        content = request.POST.get(
            "content",
            ""
        ).strip()

        if content:

            SecretNote.objects.create(
                user=request.user,
                title=title,
                content=content
            )

            return redirect("secret_notes")

    return render(
        request,
        "tracker/secret_notes.html",
        {
            "notes": notes
        }
    )


@login_required(login_url="/login/")
def delete_secret_note(
    request,
    note_id
):

    if request.method == "POST":

        note = SecretNote.objects.filter(
            id=note_id,
            user=request.user
        ).first()

        if note:

            note.delete()

    return redirect("secret_notes")