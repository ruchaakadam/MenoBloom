from django.shortcuts import render, redirect
from django.db.models import Sum
from django.db.models.functions import TruncWeek

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import SymptomEntry, UserProfile


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

    # If profile is not completed,
    # don't allow direct access to dashboard.
    if not profile.onboarding_completed:

        return redirect("choose_role")

    # ONLY this user's symptoms
    symptoms = SymptomEntry.objects.filter(
        user=request.user
    ).order_by("-date")

    total_symptoms = symptoms.count()

    health_reminders = 0

    context = {
        "symptoms": symptoms,
        "total_symptoms": total_symptoms,
        "health_reminders": health_reminders,
        "profile": profile,
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


# ============================================================
# ANALYSIS
# ============================================================

@login_required(login_url="/login/")
def analysis(request):

    # ONLY current user's symptoms
    weekly_queryset = (

        SymptomEntry.objects

        .filter(
            user=request.user
        )

        .annotate(
            week=TruncWeek("date")
        )

        .values(
            "week",
            "symptom"
        )

        .annotate(
            total_frequency=Sum(
                "frequency"
            )
        )

        .order_by(
            "week"
        )
    )

    weekly_data = []

    for item in weekly_queryset:

        weekly_data.append({

            "week":
                item["week"].strftime(
                    "%Y-%m-%d"
                ),

            "symptom":
                item["symptom"],

            "frequency":
                item["total_frequency"]
        })

    return render(

        request,

        "tracker/analysis.html",

        {
            "weekly_data": weekly_data
        }
    )


# ============================================================
# HEALTH REMINDERS
# ============================================================

@login_required(login_url="/login/")
def reminders(request):

    return render(
        request,
        "tracker/reminders.html"
    )


# ============================================================
# FOOD & LIFESTYLE
# ============================================================

@login_required(login_url="/login/")
def food(request):

    return render(
        request,
        "tracker/food.html"
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
# FAMILY DASHBOARD
# ============================================================

@login_required(login_url="/login/")
def family(request):

    profile = get_profile(
        request.user
    )

    if not profile.onboarding_completed:

        return redirect(
            "choose_role"
        )

    if profile.role != "family":

        return redirect(
            "dashboard"
        )

    return render(

        request,

        "tracker/family.html",

        {
            "profile": profile
        }
    )


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