from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.conf import settings
from functools import wraps
import os
from pathlib import Path

from core.auth import api_login_required
from team2.models import Lesson, UserDetails, VideoFiles

TEAM_NAME = "team2"


def teacher_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'لطفا ابتدا وارد شوید.')
            return redirect('auth')
        
        try:
            user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
            if user_details.role != 'teacher':
                messages.error(request, 'فقط معلم‌ها دسترسی به این صفحه دارند.')
                return redirect('team2_ping')
        except UserDetails.DoesNotExist:
            messages.error(request, 'پروفایل یافت نشد. لطفا با مدیر تماس بگیرید.')
            return redirect('team2_ping')
        return view_func(request, *args, **kwargs)
    return wrapper


@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})

def base(request):
    return render(request, f"{TEAM_NAME}/index.html")

@api_login_required
@require_http_methods(["GET"])
def lessons_list_view(request):
    from team2.models import UserDetails
    
    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
        lessons = user_details.lessons.filter(
            is_deleted=False,
            status='published'
        ).prefetch_related('videos')
    except UserDetails.DoesNotExist:
        lessons = Lesson.objects.none()

    context = {
        'lessons': lessons,
        'total_lessons': lessons.count(),
    }

    return render(request, 'team2_Lessons_list.html', context)

@api_login_required
@require_http_methods(["GET"])
def lesson_details_view(request, lesson_id):

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id,
        is_deleted=False,
        status='published'
    )

    videos = lesson.videos.filter(is_deleted=False).order_by('-uploaded_at')

    context = {
        'lesson': lesson,
        'videos': videos,
        'total_videos': videos.count(),
    }
    # TODO : create team2_lesson_details.html
    return render(request, 'team2_lesson_details.html', context)


@api_login_required
@teacher_required
@require_http_methods(["GET"])
def teacher_lessons_view(request):

    try:
        user_details = UserDetails.objects.using('team2').get(user_id=request.user.id)
        lessons = user_details.lessons.filter(is_deleted=False).prefetch_related('videos')
    except UserDetails.DoesNotExist:
        lessons = Lesson.objects.none()

    context = {
        'lessons': lessons,
        'total_lessons': lessons.count(),
    }
    return render(request, 'team2_teacher_lessons.html', context)