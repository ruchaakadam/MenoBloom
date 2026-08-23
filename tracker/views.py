from django.shortcuts import render, redirect
from django.db.models.functions import TruncWeek
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import SymptomEntry


# ============================================================
# DASHBOARD
# ============================================================

@login_required(login_url="/login/")
def dashboard(request):

    symptoms = SymptomEntry.objects.all().order_by("-date")

    total_symptoms = symptoms.count()

    # We will connect real reminders later
    health_reminders = 0

    role = request.session.get("role", "woman")

    context = {
        "symptoms": symptoms,
        "total_symptoms": total_symptoms,
        "health_reminders": health_reminders,
        "role": role,
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

    if request.method == "POST":

        selected_symptoms = request.POST.getlist("symptoms")

        for symptom in selected_symptoms:

            severity = request.POST.get(
                f"severity_{symptom}",
                "Mild"
            )

            frequency = request.POST.get(
                f"frequency_{symptom}",
                1
            )

            date = request.POST.get("date")

            notes = request.POST.get(
                "notes",
                ""
            )

            try:
                frequency = int(frequency)

            except (ValueError, TypeError):
                frequency = 1

            SymptomEntry.objects.create(
                symptom=symptom,
                severity=severity,
                frequency=frequency,
                date=date,
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

    weekly_queryset = (
        SymptomEntry.objects
        .annotate(
            week=TruncWeek("date")
        )
        .values(
            "week",
            "symptom"
        )
        .annotate(
            total_frequency=Sum("frequency")
        )
        .order_by("week")
    )

    weekly_data = []

    for item in weekly_queryset:

        weekly_data.append({
            "week": item["week"].strftime("%Y-%m-%d"),
            "symptom": item["symptom"],
            "frequency": item["total_frequency"]
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

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("choose_role")

        return render(
            request,
            "tracker/login.html",
            {
                "error": "Invalid username or password."
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

        return redirect("choose_role")

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

        # ----------------------------------------------------
        # Check password
        # ----------------------------------------------------

        if password != confirm_password:

            return render(
                request,
                "tracker/signup.html",
                {
                    "error": "Passwords do not match."
                }
            )

        # ----------------------------------------------------
        # Check username
        # ----------------------------------------------------

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "tracker/signup.html",
                {
                    "error": "Username already exists."
                }
            )

        # ----------------------------------------------------
        # Create user
        # ----------------------------------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # ----------------------------------------------------
        # Automatically login after signup
        # ----------------------------------------------------

        login(
            request,
            user
        )

        request.session.pop("role", None)

        request.session.modified = True

        return redirect("choose_role")

    return render(
        request,
        "tracker/signup.html"
    )


# ============================================================
# CHOOSE ROLE
# ============================================================

@login_required(login_url="/login/")
def choose_role(request):

    return render(
        request,
        "tracker/choose_role.html"
    )


# ============================================================
# SET ROLE
# ============================================================

@login_required(login_url="/login/")
def set_role(request, role):

    # Only two roles are allowed
    if role not in ["woman", "family"]:

        return redirect("choose_role")

    # Save selected role in session
    request.session["role"] = role

    request.session.modified = True

    # --------------------------------------------------------
    # WOMAN
    # --------------------------------------------------------
    if role == "woman":

     return redirect("woman_onboarding")

   

    return render(
        request,
        "tracker/woman_onboarding.html"
    )
    # --------------------------------------------------------
    # FAMILY MEMBER
    # --------------------------------------------------------

    if role == "family":

        return redirect("family")


# ============================================================
# FAMILY DASHBOARD
# ============================================================

@login_required(login_url="/login/")
def family(request):

    role = request.session.get(
        "role",
        "family"
    )

    context = {
        "role": role
    }

    return render(
        request,
        "tracker/family.html",
        context
    )


# ============================================================
# LOGOUT
# ============================================================

def logout_view(request):

    logout(request)

    return redirect("login")
def menopause_info(request):
    return render(
        request,
        "tracker/menopause_info.html"
    )

@login_required(login_url="/login/")
def woman_onboarding(request):

    if request.method == "POST":

        age = request.POST.get("age")

        period_status = request.POST.get(
            "period_status"
        )

        period_changes = request.POST.getlist(
            "period_changes"
        )

        symptoms = request.POST.getlist(
            "symptoms"
        )


        # ---------------------------------------------
        # Estimate the stage
        # ---------------------------------------------

        if period_status == "12_months":

            stage = "postmenopause"

        elif period_status in [
            "irregular",
            "months_missing"
        ]:

            stage = "perimenopause"

        elif period_status == "regular":

            stage = "premenopause"

        else:

            stage = "unknown"


        request.session["age"] = age

        request.session["period_status"] = (
            period_status
        )

        request.session["period_changes"] = (
            period_changes
        )

        request.session["onboarding_symptoms"] = (
            symptoms
        )

        request.session["menopause_stage"] = (
            stage
        )


        return redirect(
            "stage_result"
        )


    return render(
        request,
        "tracker/woman_onboarding.html"
    )
@login_required(login_url="/login/")
def woman_onboarding(request):

    if request.method == "POST":

        age = request.POST.get("age")
        stage = request.POST.get("stage")

        request.session["age"] = age
        request.session["menopause_stage"] = stage

        return redirect("dashboard")

    return render(
        request,
        "tracker/woman_onboarding.html"
    )