from django.urls import path
from . import views

urlpatterns = [

    # HOME
    path(
        "",
        views.home,
        name="home"
    ),

    # LOGIN
    path(
        "login/",
        views.login_view,
        name="login"
    ),

    # SIGN UP
    path(
        "signup/",
        views.signup,
        name="signup"
    ),

    # LOGOUT
    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    # ROLE SELECTION
    path(
        "choose-role/",
        views.choose_role,
        name="choose_role"
    ),

    path(
        "set-role/<str:role>/",
        views.set_role,
        name="set_role"
    ),

    # WOMAN DETAILS
    path(
        "woman-onboarding/",
        views.woman_onboarding,
        name="woman_onboarding"
    ),

    # DASHBOARD
    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),

    # SYMPTOMS
    path(
        "add-symptom/",
        views.add_symptom,
        name="add_symptom"
    ),

    # ANALYSIS
    path(
        "analysis/",
        views.analysis,
        name="analysis"
    ),

    # REMINDERS
    path(
        "reminders/",
        views.reminders,
        name="reminders"
    ),

    # FOOD
    path(
        "food/",
        views.food,
        name="food"
    ),

    # FAMILY
    path(
        "family/",
        views.family,
        name="family"
    ),

    # MENOPAUSE INFORMATION
    path(
        "menopause/",
        views.menopause_info,
        name="menopause_info"
    ),
    path(
    "gynecologist/",
    views.gynecologist,
    name="gynecologist"
),
]
