from django.urls import path
from . import views

urlpatterns = [
    path("", views.base),
    path("ping/", views.ping, name="team2_ping"),
    path("lessons/", views.lessons_list_view, name="team2_lessons_list"),
    path("lessons/rating/", views.lessons_with_rating_view, name="team2_lessons_rating"),
    path("lessons/<int:lesson_id>/", views.lesson_details_view, name="team2_lesson_details"),
    
    # Teacher URLs
    path("teacher/lessons/", views.teacher_lessons_view, name="team2_teacher_lessons"),
    path("teacher/lessons/create/", views.teacher_create_lesson_view, name="teacher_create_lesson"),
    path("teacher/lessons/<int:lesson_id>/videos/", views.teacher_lesson_videos_view, name="teacher_lesson_videos"),
    path("teacher/lessons/<int:lesson_id>/add-video/", views.add_video_view, name="teacher_add_video"),
    
    # Admin URLs
    path("admin/users/", views.admin_users_view, name="admin_users"),
    path("admin/users/<int:user_id>/change-role/", views.admin_change_role_view, name="admin_change_role"),

    # Rating API URLs
    path("api/lessons/<int:lesson_id>/rate/", views.rate_lesson_api, name="rate_lesson_api"),
    path("api/lessons/<int:lesson_id>/ratings/", views.lesson_ratings_api, name="lesson_ratings_api"),
]