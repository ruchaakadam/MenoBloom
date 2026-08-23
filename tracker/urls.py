from django.urls import path

from . import views


urlpatterns = [

    # ========================================================
    # MAIN
    # ========================================================
     path("", views.login_view, name="home"),

    # ========================================================
    # SYMPTOMS
    # ========================================================

    path(
        "add-symptom/",
        views.add_symptom,
        name="add_symptom"
    ),

    # ========================================================
    # ANALYSIS
    # ========================================================

    path(
        "analysis/",
        views.analysis,
        name="analysis"
    ),

    # ========================================================
    # REMINDERS
    # ========================================================

    path(
        "reminders/",
        views.reminders,
        name="reminders"
    ),

    # ========================================================
    # FOOD
    # ========================================================

    path(
        "food/",
        views.food,
        name="food"
    ),

    # ========================================================
    # AUTHENTICATION
    # ========================================================

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "signup/",
        views.signup,
        name="signup"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    # ========================================================
    # ROLE SELECTION
    # ========================================================

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

    # ========================================================
    # FAMILY
    # ========================================================

    path(
        "family/",
        views.family,
        name="family"
    ),

    path("menopause/", views.menopause_info, name="menopause_info"),

    path("dashboard/", views.dashboard, name="dashboard"),
    
     path(
    "woman-onboarding/",
    views.woman_onboarding,
    name="woman_onboarding"
),
    
]