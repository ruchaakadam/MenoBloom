from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("login/", views.login_view, name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),

    path("choose-role/", views.choose_role, name="choose_role"),
    path("set-role/<str:role>/", views.set_role, name="set_role"),
    path("woman-onboarding/", views.woman_onboarding, name="woman_onboarding"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("add-symptom/", views.add_symptom, name="add_symptom"),
    path("analysis/", views.analysis, name="analysis"),

    path("reminders/", views.reminders, name="reminders"),
    path("reminders/add/", views.add_reminder, name="add_reminder"),
    path(
        "reminders/<int:reminder_id>/complete/",
        views.complete_reminder,
        name="complete_reminder"
    ),
    path(
        "reminders/<int:reminder_id>/delete/",
        views.delete_reminder,
        name="delete_reminder"
    ),
    

    path("food/", views.food, name="food"),
    path("family/", views.family, name="family"),
    path(
    "family/disconnect/",
    views.disconnect_family,
    name="disconnect_family"
),
    path("menopause/", views.menopause_info, name="menopause_info"),
    path("gynecologist/", views.gynecologist, name="gynecologist"),
# ============================================================
# MENTAL SUPPORT
# ============================================================

path(
    "mental-support/",
    views.mental_support,
    name="mental_support"
),


# ============================================================
# SECRET NOTES
# ============================================================

path(
    "secret-notes/",
    views.secret_notes,
    name="secret_notes"
),

path(
    "secret-notes/<int:note_id>/delete/",
    views.delete_secret_note,
    name="delete_secret_note"
),

path(
    "report-analysis/",
    views.report_analysis,
    name="report_analysis"
),

path(
    "report-result/<int:report_id>/",
    views.report_result,
    name="report_result"
),

path(
    "previous-reports/",
    views.previous_reports,
    name="previous_reports"
),
]

