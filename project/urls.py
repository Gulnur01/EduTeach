"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django import urls
from django.urls import path, re_path
from mysite  import views
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, re_path
from django.urls import path, include
from django.urls import re_path
from mysite import consumers

 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.profil, name='profil'),
    path('index/', views.index, name='index'),
    path('home/', views.profile_view, name='home'),
    path("class1/", views.class1, name="class1"),
    path('students/<int:post_id>/', views.show_post, name='post'),
    path('save_grade/', views.save_grade, name='save_grade'),
    path('ktp/', views.plan, name='plan'),
    path('add_ktp/', views.add_ktp, name='add_ktp'),
    path('quarters/', views.quarters_list_view, name='quarters_list'),
    path('meeting_room/', views.meeting_room, name='meeting_room'),
    path('meeting/',views.videocall, name='meeting'),
    path('meeting_room/<int:receiver_id>/', views.chat_with_user, name='detail'),  
    path('model_view/', views.model_viewer, name='model_view'),
    path('processor/<int:model_id>/', views.get_model_data, name='processor_model'),
    path('parameter/', views.teacher_dashboard, name='teacher_dashboard'),
    path('tasks/', views.tasks, name='tasks'),
    path('video/<int:ktp_id>/', views.video_detail, name='video_detail'),  # для просмотра видеоурока
    path('task_detail/<int:ktp_id>/', views.task_detail, name='task_detail'), 
    path('add_lesson/<int:ktp_id>/', views.add_lesson_and_test, name='add_lesson_and_test'),
    path('lesson/', views.ktp_with_lessons, name='lesson'),
    path('information/<int:lesson_id>/', views.information, name='information'),
    path('message/', views.message, name='message'),
    path('conversation/<int:conv_id>/', views.conversation, name='conversation'),
    path('grades/', views.grades_view, name='grades_view'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    #path('task_detail/', views.task_detail, name='task_detail '),
    path('zadanie/<int:ktp_id>/<int:task_type_id>/', views.create_task, name='create_task'),
    path('run-code/', views.run_code, name='run_code'),
    path('test_view/<int:task_id>/', views.test_view, name='test_view'),
    path('test_view/<int:task_id>/submit/', views.submit_test, name='submit_test'),
    path('retake_view/<int:task_id>/', views.retake_view, name='retake_view'),
    path('retake_view/<int:task_id>/submit/', views.retake_test, name='retake_test'),
    path('latest_written_task/<int:lesson_id>/', views.latest_written_task, name='latest_written_task'),
    path("exercise/<int:lesson_id>/", views.latest_code_task, name="latest_code_task"),
    path('homework/', views.homework, name='homework'),
    path('homework/task/<int:task_type_id>/', views.written_view, name='written_view'),
    path('writework/<int:class_id>/', views.writework, name='writework'),
    path('testwork/<int:class_id>/', views.testwork, name='testwork'),
    path('codework/<int:class_id>/', views.codework, name='codework'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)   

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)