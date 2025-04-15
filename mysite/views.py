from pyexpat.errors import messages
import random
import tempfile
from django import test
from django.contrib import messages
import subprocess
from django.dispatch import receiver
from django.forms import model_to_dict
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.db.models import Q
from dotenv import load_dotenv
import openai  # Q обьектісін импорттау
from mysite.forms import ChatMessageForm, ImageUploadForm, VideoLessonForm, VideoTestForm
from .models import Answer, ClassModel, CodeTask, CodeTaskSubmission, Question, StudentAnswer, TaskType, TestAttempt, Testview, ThreeDModel, VideoLesson, VideoTest, WrittenTask, WrittenTaskSubmission
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import Login
from .models import Student, Quarter, Ktp, Teacher
from django.contrib.auth.hashers import check_password 
from datetime import datetime, timedelta, timezone
import json
from django.http import JsonResponse
from django.http import JsonResponse
from django.shortcuts import render
from .models import Student, Grade, ChatMessage, Profile, Friend
from datetime import date
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
import os
import numpy as np
from PIL import Image
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from mysite import models
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min, Avg
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils.timezone import now
from .models import TestResult
from django.utils import timezone


def index(request):
    return render(request, "index.html")

def class1(request):
    classmodel = ClassModel.objects.all()
    return render(request, "class1.html", {"classmodel": classmodel})

def show_post(request, post_id):
    # Получаем объект класса по его ID
    classmodel = get_object_or_404(ClassModel, id=post_id)
    
    # Получаем всех студентов этого класса
    students = classmodel.students.all()  # Все студенты для этого класса

    # Для каждого студента получаем его оценки
    student_grades = []
    for student in students:
        grades = student.grades.all()  # Все оценки для текущего студента
        
        # Убедитесь, что количество оценок соответствует количеству дат
        student_grades.append({
            'student': student,
            'grades': grades  # Здесь предполагается, что оценки идут по порядку (12.қаз, 19.қаз, и т.д.)
        })

    # Передаем данные в шаблон
    return render(request, "students.html", {"classmodel": classmodel, 'student_grades': student_grades})

def home(request):
    profiles = Login.objects.all()  # Извлекаем все объекты из модели Login
    return render(request, 'students/home.html', {'profiles': profiles})  # Передаем данные в шаблон

def save_grade(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        date_part = request.POST.get('date')  # Пример: "12_kaz"
        grade_value = request.POST.get('grade')

        # Проверка входных данных
        if not student_id or not date_part or not grade_value:
            return JsonResponse({'error': 'Неверные данные'}, status=400)

        try:
            grade_value = int(grade_value)
        except ValueError:
            return JsonResponse({'error': 'Оценка должна быть числом'}, status=400)

        # Определяем дату (например, из "12_kaz" берём "12")
        try:
            date = datetime.strptime(date_part[:2], "%d").replace(year=2024, month=1)
        except ValueError:
            return JsonResponse({'error': 'Некорректный формат даты'}, status=400)

        # Получаем студента
        student = get_object_or_404(Student, id=student_id)

        # Сохраняем или обновляем оценку
        grade, created = Grade.objects.update_or_create(
            student=student,
            date=date,
            defaults={'grade': grade_value},
        )

        return JsonResponse({'success': 'Оценка успешно сохранена!'})

    return JsonResponse({'error': 'Неверный метод запроса'}, status=405)

def plan(request):
    ktps = Ktp.objects.all()
    return render(request, 'ktp.html', {'ktps': ktps})  # Передаем данные в шаблон

def add_ktp(request):
    if request.method == 'POST':
        try:
            data = {
                'number': request.POST['number'],
                'tema': request.POST['tema'],
                'purpose': request.POST['purpose'],
                'number_of_hours': request.POST['number_of_hours'],
                'date': request.POST['date'],
                'homework': request.POST['homework'],
            }

            quarter_id = request.POST['quarter']
            quarter = Quarter.objects.get(pk=quarter_id)
            ktp = Ktp(quarter1=quarter, **data)
            ktp.save()
            return JsonResponse({'success': True})  # Возвращаем JSON-ответ
        except (KeyError, ValueError, Quarter.DoesNotExist) as e:
            return JsonResponse({'error': str(e)}, status=400)  # Возвращаем ошибку в JSON
    else:
        quarters = Quarter.objects.all()
        return render(request, 'ktp1.html', {'quarters': quarters})
    
def quarters_list_view(request):
    quarters = Quarter.objects.prefetch_related('ktps')  # Предзагрузка связанных Ktp
    return render(request, 'ktp.html', {
        'quarters': quarters,
    })
    
def meeting_room(request):
    user = request.user.profile
    friends = user.friends.all()
    context = {"user": user, "friends": friends}
    return render(request, "meeting_room.html", context) 

def videocall(request):
    # Проверяем, что пользователь аутентифицирован
    if request.user.is_authenticated:
        full_name = f"{request.user.first_name} {request.user.last_name}".strip()
    else:
        full_name = "Гость"  # Или любое другое значение по умолчанию

    return render(
        request,
        'videocall.html',
        {'name': full_name},
    )
def profil(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:  # Проверка, что пользователь найден
            login(request, user)  # Здесь передаем объект user
            if user.groups.filter(name='teacher').exists():
                return redirect('index')  # Перенаправление на страницу учителя
            elif user.groups.filter(name='student').exists():
                return redirect('home')  # Перенаправление на страницу студента
            else:
                return render(request, 'login.html', {'error_message': 'У вас нет роли'})
        else:
            return render(request, 'login.html')

    return render(request, 'login.html')


@login_required
def chat_with_user(request, receiver_id):
    sender = request.user.profile  # Жіберуші профилін алу
    receiver = get_object_or_404(Profile, id=receiver_id)  # Алушы профилін тексеру

    if request.method == 'POST':
        # Пайдаланушыдан хабарлама мәтінін алу
        body = request.POST.get('message')
        if body:
            # Хабарламаны дерекқорға сақтау
            new_message = ChatMessage.objects.create(
                body=body,
                msg_sender=sender,
                msg_receiver=receiver
            )
            # Жауапты JSON форматында қайтарамыз
            return JsonResponse({
                'success': True,
                'body': new_message.body,
                'msg_sender': new_message.msg_sender.name,
                'msg_receiver': new_message.msg_receiver.name,
                'timestamp': new_message.id,  # Қажет болса, уақыт белгісін қосыңыз
            })

        # Егер хабарлама бос болса, сәтсіз жауап қайтарамыз
        return JsonResponse({'success': False, 'error': 'Message is empty'})

    # GET әдісі үшін чат хабарламаларын көрсету
    messages = ChatMessage.objects.filter(
        (Q(msg_sender=sender) & Q(msg_receiver=receiver)) |
        (Q(msg_sender=receiver) & Q(msg_receiver=sender))
    ).order_by('id')

    # Контекстті шаблонға жіберу
    context = {
        'receiver': receiver,
        'messages': messages,
    }
    return render(request, 'meeting_room.html', context)

def model_viewer(request):
    models = ThreeDModel.objects.all()  # Барлық модельдерді алу
    return render(request, 'model_view.html', {'models': models})

def get_model_data(request, model_id):
    model = ThreeDModel.objects.get(id=model_id)
    return render(request, 'processor_model.html', {'model': model})

@login_required
def teacher_dashboard(request):
    # Мұғалімнің профилін алу
    try:
        teacher = request.user.teacher_profile  # related_name='teacher_profile'
    except:
        teacher = None

    return render(request, 'parametr.html', {'teacher': teacher})

def profile_view(request):
    # Получение текущего пользователя
    profile = Profile.objects.get(user=request.user)
    
    # Данные пользователя
    user_data = {
        'name': profile.name,
        'image_url': profile.pic.url if profile.pic else None,
        'username': profile.user.username,
        'first_name': profile.user.first_name,
        'last_name': profile.user.last_name,
        'email':profile.user.email,
        'date':profile.user.date_joined,
        'password': profile.user.password,  # Пароль хранится в хэшированном виде
    }

    return render(request, 'students/home.html', {'user_data': user_data})   

def tasks(request):
    topics=Ktp.objects.all()
    return render(request, "tasks.html", {'topics': topics})

def video_detail(request, ktp_id):
    # Получаем урок по ID Ktp
    lesson = get_object_or_404(VideoLesson, addlesson__id=ktp_id)
    # Получаем вопросы для этого урока
    questions = VideoTest.objects.filter(lesson=lesson)
    ktp = lesson.addlesson
    return render(request, 'addlessons.html', {
        'lesson': lesson,
        'questions': questions,  # Отправляем вопросы на шаблон
        'ktp': ktp
    })

def task_detail(request, ktp_id):
    ktp = get_object_or_404(Ktp, id=ktp_id)
    task_types = TaskType.objects.all()
    return render(request, 'task_detail.html', {'ktp': ktp, 'task_types': task_types})

def add_lesson_and_test(request, ktp_id):
    ktp = get_object_or_404(Ktp, id=ktp_id)
    lesson_id = None

    if request.method == 'POST':
        # Видео сабақты сақтау
        if 'video_lesson' in request.POST:
            description = request.POST.get('video_description')
            video_file = request.FILES.get('video_file')
            duration = request.POST.get('duration')

            try:
                duration = int(duration) if duration else 0
            except ValueError:
                duration = 0

            if video_file:
                video_lesson = VideoLesson.objects.create(
                    addlesson=ktp,
                    description=description,
                    video_file=video_file,
                    duration=duration
                )
                messages.success(request, 'Видео-сабақ успешно добавлен!')
                # Сақталған видео сабақтың ID-сын контекстке қосу
                lesson_id = video_lesson.id
            else:
                messages.error(request, 'Пожалуйста, выберите файл для видео.')

        # Тестті сақтау
        if 'video_test' in request.POST:
            lesson_id = request.POST.get('lesson_id')

            if lesson_id and lesson_id.isdigit():
                lesson = VideoLesson.objects.filter(id=lesson_id, addlesson=ktp).first()

                if lesson:
                    timestamp = request.POST.get('timestamp')
                    question = request.POST.get('question')
                    correct_answer = request.POST.get('correct_answer')
                    options = request.POST.get('options')

                    lesson_id = request.POST.get('lesson_id')

                    if not lesson_id:
                        messages.error(request, 'Урок таңдалмаған!')
                        return redirect('add_lesson_and_test', ktp_id=ktp.id)

                    try:
                        timestamp = int(timestamp)
                        options_list = options.split(",")

                        # JSONField-ға тізімді береміз
                        video_test = VideoTest.objects.create(
                            lesson=lesson,
                            timestamp=timestamp,
                            question=question,
                            correct_answer=correct_answer,
                            options=options_list
                        )
                        messages.success(request, 'Вопрос успешно добавлен!')
                    except ValueError:
                        messages.error(request, 'Некорректные данные для timestamp. Убедитесь, что timestamp — это число.')
                else:
                    messages.error(request, 'Урок с указанным ID не найден.')
            else:
                messages.error(request, 'Некорректный ID урока.')

        return redirect('add_lesson_and_test', ktp_id=ktp.id)

    return render(request, 'addlessons.html', {'ktp': ktp, 'lesson_id': lesson_id})

def ktp_with_lessons(request):
    video_lessons = VideoLesson.objects.select_related('addlesson').all()
    return render(request, 'students/lessons.html', {'video_lessons': video_lessons})

def information(request, lesson_id):
    # Өзіңіз таңдаған VideoLesson-ды аламыз
    lesson = get_object_or_404(VideoLesson, id=lesson_id)
    tests = VideoTest.objects.filter(lesson=lesson).order_by('timestamp')
    # Ktp моделінің purpose өрісін бөлу
    purpose = lesson.addlesson.purpose.split("? ")  # purpose-ты split етіп, тізімге айналдыру

    # Барлық VideoLesson жазбаларын аламыз
    stages = VideoLesson.objects.all()

    # Әрбір stage үшін description мәліметін бөлу
    for stage in stages:
        # Егер stage-де description өрісі болса, оны split ету
        if hasattr(stage, 'description'):
            stage_description = stage.description.split("? ")
            stage.split_description = stage_description  # Бөлінген мәліметті қосамыз
    
    ktps = Ktp.objects.all()
    
    # Мәліметтерді шаблонға жіберу
    return render(request, 'students/information.html', {
        'lesson': lesson,
        'tests': tests,
        'purpose': purpose,
        'stages': stages,
        'ktps': ktps
    })

def message(request):
    user = request.user.profile
    friends = user.friends.all()
    context = {"user": user, "friends": friends}
    return render(request, "students/conversation.html", context) 

@login_required
def conversation(request, conv_id):
    
    user = request.user.profile
    friends = user.friends.all()
    
    sender = request.user.profile  # Жіберуші профилін алу
    receiver = get_object_or_404(Profile, id=conv_id)  # Алушы профилін тексеру

    if request.method == 'POST':
        # Пайдаланушыдан хабарлама мәтінін алу
        body = request.POST.get('message')
        if body:
            # Хабарламаны дерекқорға сақтау
            new_message = ChatMessage.objects.create(
                body=body,
                msg_sender=sender,
                msg_receiver=receiver
            )
            # Жауапты JSON форматында қайтарамыз
            return JsonResponse({
                'success': True,
                'body': new_message.body,
                'msg_sender': new_message.msg_sender.name,
                'msg_receiver': new_message.msg_receiver.name,
                'timestamp': new_message.id,  # Қажет болса, уақыт белгісін қосыңыз
            })

        # Егер хабарлама бос болса, сәтсіз жауап қайтарамыз
        return JsonResponse({'success': False, 'error': 'Message is empty'})

    # GET әдісі үшін чат хабарламаларын көрсету
    messages = ChatMessage.objects.filter(
        (Q(msg_sender=sender) & Q(msg_receiver=receiver)) |
        (Q(msg_sender=receiver) & Q(msg_receiver=sender))
    ).order_by('id')

    # Контекстті шаблонға жіберу
    context = {
        'receiver': receiver,
        'messages': messages,
        "user": user, 
        "friends": friends
    }
    return render(request, 'students/conversation.html', context)

def calculate_average(grades):
    if grades.exists():
        return grades.aggregate(Avg('grade'))['grade__avg']
    return 0  # Возвращает 0, если нет оценок

@login_required
def grades_view(request):
    try:
        student = Student.objects.get(login=request.user)
    except Student.DoesNotExist:
        raise Http404("Студент не найден. Пожалуйста, создайте запись студента.")
    
    # Получаем все оценки для студента
    user_grades = Grade.objects.filter(student=student)

    # Создаем контекст с данными для отображения
    context = {
        'grades': user_grades,
        'average_grade': calculate_average(user_grades),
        'total_grades': user_grades.count(),
        'highest_grade': user_grades.aggregate(Max('grade'))['grade__max'],
        'lowest_grade': user_grades.aggregate(Min('grade'))['grade__min'],
    }

    # Передаем контекст в шаблон
    return render(request, 'students/zhurnal.html', context)

# Views
def lesson_view(request, lesson_id):
    lesson = VideoLesson.objects.get(id=lesson_id)
    questions = lesson.questions.all()
    return render(request, 'addLessons.html', {
        'lesson': lesson,
        'questions': questions
    })

@csrf_exempt
def check_answer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question_id = data.get('question_id')
        selected_option = data.get('selected_option')

        question = VideoTest.objects.get(id=question_id)
        if question.correct_option == selected_option:
            return JsonResponse({'correct': True})
        else:
            return JsonResponse({'correct': False, 'correct_option': question.correct_option})
        
def save_code(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        print("Сохраненный код:", code)

        return JsonResponse({'message': 'Код сохранен успешно!'})
    else:
        return JsonResponse({'error': 'Метод не поддерживается'}, status=400)


def run_code(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        code = data.get('code', '')
        input_data = data.get('input_data', '')

        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
            temp_file.write(code.encode('utf-8'))
            temp_file_path = temp_file.name

        try:
            process = subprocess.Popen(
                ['python', temp_file_path],  # `python` — универсально, можно `python3`, если нужно
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output, error = process.communicate(input=input_data, timeout=5)

            if error:
                return JsonResponse({'result': f'Ошибка выполнения:\n{error}'})
            return JsonResponse({'result': output})
        except subprocess.TimeoutExpired:
            return JsonResponse({'result': 'Превышено время выполнения!'})
        finally:
            try:
                os.remove(temp_file_path)  # <-- Вот это правильный способ удаления
            except Exception as e:
                print(f"Ошибка при удалении временного файла: {e}")
    else:
        return JsonResponse({'result': 'Метод не поддерживается'})
        
def create_task(request, ktp_id, task_type_id):
    ktp = get_object_or_404(Ktp, id=ktp_id)  # Получаем Ktp
    task_type = get_object_or_404(TaskType, id=task_type_id)  # Получаем тип задачи

    if request.method == 'POST':
        print(request.POST)  # Посмотрим, какие данные приходят
        if task_type.name == "Тест":
            questions_data = []  # Список для всех вопросов
            test = Testview.objects.create(lesson=ktp, tasktype=task_type)  # Создаем тест

            for i in range(1, 11):  # 10 вопросов
                question_text = request.POST.get(f'question{i}')  # Получаем текст вопроса
                options = [
                    request.POST.get(f'option{i}_1'),
                    request.POST.get(f'option{i}_2'),
                    request.POST.get(f'option{i}_3'),
                    request.POST.get(f'option{i}_4')
                ]
                correct_answer = request.POST.get(f'correct{i}')  # Получаем правильный ответ

                if question_text and all(options) and correct_answer is not None:
                    # Создаем вопрос
                    question = Question.objects.create(test=test, text=question_text)
                    
                    # Создаем варианты ответов
                    for j, option in enumerate(options):
                        Answer.objects.create(question=question, text=option, is_correct=(j == int(correct_answer)))

            return HttpResponse('Тапсырма сәтті қосылды!')

        elif task_type.name == "Жазбаша":
            written_text = request.POST.get('text')
            if written_text:
                print("Текст письменного задания:", written_text)
                WrittenTask.objects.create(lesson=ktp, tasktype=task_type, text=written_text)

        if task_type.name == "Есеп":
            description = request.POST.get('description', '').strip()
            code = request.POST.get('code', '').strip()
            input_data = request.POST.get('input_data', '').strip() or ""

            if not description or not code:
                return JsonResponse({'error': 'Описание и код обязательны!'}, status=400)

        # 1. Выполнить код и получить output
            try:
                output = run_python_code(code, input_data)
            except Exception as e:
                return JsonResponse({'error': f'Ошибка выполнения кода: {str(e)}'}, status=400)

        # 2. Сохранить все данные в базу данных
            lesson = get_object_or_404(Ktp, pk=ktp_id)
            task_type = get_object_or_404(TaskType, pk=task_type_id)

            task = CodeTask.objects.create(
                lesson=lesson,
                tasktype=task_type,
                description=description,
                code=code,
                input_data=input_data or None,  # Если пусто - None
                output=output  # Вот тут сохраняем реальный вывод кода
            )

            return JsonResponse({'message': 'Задача сохранена', 'task_id': task.id})

    # Если метод не POST, отображаем форму
    return render(request, 'testview.html', {'ktp': ktp, 'task_type': task_type, 'range': range(1, 11)})

def run_python_code(code, input_data=""):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name

    try:
        process = subprocess.Popen(
            ['python', temp_file_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output, error = process.communicate(input=input_data, timeout=5)

        if error:
            return f'Ошибка выполнения:\n{error}'

        return output.strip()

    finally:
        subprocess.run(['del', temp_file_path], shell=True)  # Для Windows

def student_dashboard(request):
    student = request.user  # Қазіргі оқушы

    # Ең соңғы тапсырмаларды алу
    latest_test = Testview.objects.select_related('lesson').order_by('-generated_at').first()
    latest_written = WrittenTask.objects.select_related('lesson').order_by('-created_at').first()
    latest_code = CodeTask.objects.select_related('lesson').order_by('-created_at').first()

    # Тест тапсырмасының күйін анықтау
    test_completed = TestAttempt.objects.filter(student=student, test=latest_test).exists() if latest_test else False
    test_expired = latest_test and latest_test.generated_at < now() - timedelta(days=7)
    test_new = latest_test and latest_test.generated_at > now() - timedelta(days=1)

    # Жазбаша тапсырманың күйін анықтау
    written_completed = WrittenTaskSubmission.objects.filter(student=student, task=latest_written).exists() if latest_written else False
    written_new = latest_written and latest_written.created_at > now() - timedelta(days=1)

    # Код тапсырмасының күйін анықтау
    code_completed = CodeTaskSubmission.objects.filter(student=student, task=latest_code).exists() if latest_code else False
    code_new = latest_code and latest_code.created_at > now() - timedelta(days=1)

    latest_tasks = {
        "Тест": {"task": latest_test, "completed": test_completed, "expired": test_expired, "new": test_new},
        "Жазбаша тапсырма": {"task": latest_written, "completed": written_completed, "expired": False, "new": written_new},
        "Есеп": {"task": latest_code, "completed": code_completed, "expired": False, "new": code_new}
    }

    return render(request, 'students/test.html', {'latest_tasks': latest_tasks})

def write(request):
    return render(request, "write.html") 

def test_view(request, task_id):
    """ Отображение теста, вопрос за вопросом """
    task = get_object_or_404(Testview, id=task_id)
    lesson = task.lesson
    questions = task.questions.all().order_by('id')  # Получаем вопросы в порядке их id

    context = {
        'task': task,
        'lesson_title': lesson.tema,
        'lesson_goal': lesson.purpose,
        'questions': questions,  # Все вопросы
        'total_questions': questions.count(),
    }
    return render(request, 'students/testView.html', context)


@csrf_exempt  # Если используешь CSRF-токен, убери это и передавай токен в запросе
def submit_test(request, task_id):
    if request.method == "POST":
        data = request.POST
        score = 0
        correct_answers = 0

        test = get_object_or_404(Testview, id=task_id)  # Получаем объект теста
        total_questions = Question.objects.filter(test=test).count()

        for key, value in data.items():
            if key.startswith("question_"):
                question_id = key.split("_")[1]
                try:
                    question = Question.objects.get(id=question_id, test=test)
                    selected_answer = Answer.objects.get(id=value)

                    StudentAnswer.objects.create(
                        student=request.user,
                        question=question,
                        selected_answer=selected_answer,
                        is_correct=selected_answer.is_correct
                    )
 
                    if selected_answer.is_correct:
                        correct_answers += 1

                except (Question.DoesNotExist, Answer.DoesNotExist):
                    continue

        if total_questions > 0:
            score = round((correct_answers / total_questions) * 100, 2)

        # ✅ Исправлено: передаем объект теста, а не его ID
        TestResult.objects.create(
            student=request.user,
            test=test,  # Здесь передаем объект Testview, а не число!
            score=score
        )

        return JsonResponse({"score": score})

    return JsonResponse({"error": "Invalid request"}, status=400)

def retake_view(request, task_id):
    """ Отображение теста, вопрос за вопросом """
    task = get_object_or_404(Testview, id=task_id)
    lesson = task.lesson
    questions = task.questions.all().order_by('id')  # Получаем вопросы в порядке их id

    context = {
        'task': task,
        'lesson_title': lesson.tema,
        'lesson_goal': lesson.purpose,
        'questions': questions,  # Все вопросы
        'total_questions': questions.count(),
    }
    return render(request, 'students/retake.html', context)


@csrf_exempt  # Если используешь CSRF-токен, убери это и передавай токен в запросе
def retake_test(request, task_id):
    if request.method == "POST":
        data = request.POST
        score = 0
        correct_answers = 0

        test = get_object_or_404(Testview, id=task_id)  # Получаем объект теста
        total_questions = Question.objects.filter(test=test).count()

        for key, value in data.items():
            if key.startswith("question_"):
                question_id = key.split("_")[1]
                try:
                    question = Question.objects.get(id=question_id, test=test)
                    selected_answer = Answer.objects.get(id=value)

                    StudentAnswer.objects.create(
                        student=request.user,
                        question=question,
                        selected_answer=selected_answer,
                        is_correct=selected_answer.is_correct
                    )
 
                    if selected_answer.is_correct:
                        correct_answers += 1

                except (Question.DoesNotExist, Answer.DoesNotExist):
                    continue

        if total_questions > 0:
            score = round((correct_answers / total_questions) * 100, 2)

        # ✅ Исправлено: передаем объект теста, а не его ID
        TestResult.objects.create(
            student=request.user,
            test=test,  # Здесь передаем объект Testview, а не число!
            score=score
        )

        return JsonResponse({"score": score})

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def latest_written_task(request, lesson_id):
    task_type = get_object_or_404(TaskType, name="Жазбаша")
    
    # lesson_id бойынша ең соңғы тапсырманы алу
    task = WrittenTask.objects.filter(lesson_id=lesson_id, tasktype=task_type).order_by('-created_at').first()

    if not task:
        return render(request, 'task_not_found.html', {})

    # Егер форма жіберілген болса
    if request.method == "POST":
        answer_text = request.POST.get("text")  # Hidden input арқылы келген жауап
        
        # Жауапты жазу
        WrittenTaskSubmission.objects.create(
            student=request.user,
            task=task,
            answer_text=answer_text,
            submitted_at=now()
        )
        
        # Хабарлама көрсету
        messages.success(request, "Жауабыңыз сәтті жіберілді!")

    return render(request, 'students/write_tasks.html', {'task': task})

@login_required
def latest_code_task(request, lesson_id):
    # "Есеп" түріндегі тапсырма түрін табу
    task_type = get_object_or_404(TaskType, name="Есеп")

    # Белгілі бір сабаққа байланысты ең соңғы CodeTask табу
    task = CodeTask.objects.filter(lesson_id=lesson_id, tasktype=task_type).order_by('-created_at').first()

    if not task:
        return render(request, 'task_not_found.html', {})

    # Егер форма жіберілсе (POST)
    if request.method == "POST":
        submitted_code = request.POST.get("code", "")
        input_data = request.POST.get("input_data", "")

        CodeTaskSubmission.objects.create(
            student=request.user,
            task=task,
            submitted_code=submitted_code,
            submitted_at=now()
        )

        messages.success(request, "Кодыңыз сәтті жіберілді!")

    return render(request, 'students/code.html', {'task': task})

def homework(request):
    task_types = TaskType.objects.all()
    return render(request, 'homework.html', { 'task_types': task_types})

def written_view(request, task_type_id):
    task_type = get_object_or_404(TaskType, id=task_type_id)
    classes = ClassModel.objects.all()


    if task_type.name == "Жазбаша":
        class_url_name = 'writework'
    elif task_type.name == "Тест":
        class_url_name = 'testwork'
    elif task_type.name == "Есеп":
        class_url_name = 'codework'
    else:
        class_url_name = ''

    classes_with_counts = []

    for cls in classes:
        if task_type.name == "Жазбаша":
            student_count = cls.students.filter(
                login__writtentasksubmission__task__tasktype=task_type
            ).distinct().count()

        elif task_type.name == "Тест":
            student_count = TestResult.objects.filter(
                test__tasktype=task_type,
                student__in=cls.students.values_list('login', flat=True)
            ).values('student').distinct().count()

        elif task_type.name == "Есеп":
            student_count = cls.students.filter(
                login__codetasksubmission__task__tasktype=task_type
            ).distinct().count()
        else:
            student_count = 0

        # Барлық сыныптарды қосу, оқушы саны қандай болса да
        classes_with_counts.append({
            'class': cls,
            'url_name': class_url_name,
            'student_count': student_count
        })

    return render(request, 'classes.html', {
        'classes': classes_with_counts,
        'task_type': task_type
    })

def writework(request, class_id):
    # Класс және студенттерді алу
    class_model = get_object_or_404(ClassModel, id=class_id)
    students = Student.objects.filter(classmodel=class_model).select_related('login')

    # Студенттердің тапсырмаларын алған сабақ ID-лерін алу
    lesson_ids = WrittenTaskSubmission.objects.filter(
        student__in=[s.login for s in students]).values_list('task__lesson__id', flat=True).distinct()

    # Бағаланған студенттердің ID-лерін алу
    graded_student_ids = Grade.objects.filter(
        tema_id__in=lesson_ids, student__in=students).values_list('student__login__id', flat=True).distinct()

    # Фильтрация статусын алу (all, graded, pending)
    status = request.GET.get('status', 'all')

    # Студенттерді статус бойынша фильтрациялау
    if status == 'graded':
        # Тек бағаланған студенттерді көрсету
        students = students.filter(login__id__in=graded_student_ids)
    elif status == 'pending':
        # Тек бағаланбаған студенттерді көрсету
        students = students.exclude(login__id__in=graded_student_ids)

    # Баға қою үшін студент таңдалған болса
    selected_student_id = request.GET.get('student_id')
    student_obj = None
    submissions = []
    is_graded = False  # Студенттің тапсырмасы бағаланғаны/бағаланбағаны туралы ақпарат

    if selected_student_id:
        student_obj = get_object_or_404(Student, id=selected_student_id)
        submissions = WrittenTaskSubmission.objects.filter(student=student_obj.login)

        # Студенттің соңғы тапсырмасы бағаланғанын тексеру
        latest_submission = WrittenTaskSubmission.objects.filter(student=student_obj.login).order_by('-submitted_at').first()
        if latest_submission:
            is_graded = Grade.objects.filter(student=student_obj, tema=latest_submission.task.lesson).exists()

    # Баға қою үшін POST сұрауы
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        tema_id = request.POST.get('tema_id')
        grade_value = request.POST.get('grade')

        if student_id and tema_id and grade_value:
            student = get_object_or_404(Student, id=student_id)
            tema = get_object_or_404(Ktp, id=tema_id)

            # Егер студент әлі бағаланбаған болса ғана баға қою
            if not is_graded:
                Grade.objects.create(
                    student=student,
                    tema=tema,
                    grade=int(grade_value),
                    date=timezone.now().date()
                )
                # Баға қойылған соң бетке қайта бағыттау
                return redirect(f"{request.path}?student_id={student_id}&status={status}")
            else:
                # Егер бағаланған болса, хабарлама беру
                return HttpResponse("Бұл студенттің тапсырмасы бағаланған.")

    # Контекстті шаблонға беру
    context = {
        'class_model': class_model,
        'graded_students': students.filter(login__id__in=graded_student_ids),
        'pending_students': students.exclude(login__id__in=graded_student_ids),
        'students': students,
        'selected_student_id': selected_student_id,
        'submissions': submissions,
        'student_obj': student_obj,
        'is_graded': is_graded,
        'status': status  # Фильтрация статусын контекстке қосу
    }

    return render(request, 'writework.html', context)

def testwork(request, class_id):
    class_model = get_object_or_404(ClassModel, id=class_id)
    
    # Студенттерді алу
    students = Student.objects.filter(classmodel=class_model)
    
    # Сабақтардың ID-сі (тек тестпен байланысты сабақтар)
    lesson_ids = StudentAnswer.objects.filter(
        student__in=[s.login for s in students]
    ).values_list('question__test__lesson__id', flat=True).distinct()
    
    # Бағаланған студенттердің ID-сі
    graded_student_ids = Grade.objects.filter(
        tema_id__in=lesson_ids,
        student__in=students
    ).values_list('student__login__id', flat=True).distinct()
    
    # Фильтр бойынша сұрыптау
    status = request.GET.get("status", "all")
    if status == "graded":
        students = students.filter(login__id__in=graded_student_ids)
    elif status == "pending":
        students = students.exclude(login__id__in=graded_student_ids)
    
    # Таңдалған студенттің ID-сі
    selected_student_id = request.GET.get("student_id")
    submissions = []

    selected_student = None
    if selected_student_id:
        # Студентті алу, бірақ студенттің login арқылы User моделін алу
        student_user = get_object_or_404(Student, id=selected_student_id)
        selected_student = student_user
        
        # Барлық тесттерді алу (тек осы классқа қатысы бар сабақтар)
        tests = Testview.objects.filter(lesson__id__in=lesson_ids)

        for test in tests:
            # Соңғы 10 StudentAnswer алу
            student_answers = StudentAnswer.objects.filter(
                student=student_user.login,  # 'login' арқылы User моделіне сілтеме жасау
                question__test=test
            ).order_by('-created_at')[:10]  # Соңғы 10 сұрақ

            question_data = []
            correct = 0
            incorrect = 0

            for answer in student_answers:
                correct_answers = [a.text for a in answer.question.answers.filter(is_correct=True)]
                all_answers = [a.text for a in answer.question.answers.all()]

                question_data.append({
                    "question_text": answer.question.text,
                    "selected_answer": answer.selected_answer.text,
                    "is_correct": answer.is_correct,
                    "correct_answers": correct_answers,
                    "all_answers": all_answers,
                })

                if answer.is_correct:
                    correct += 1
                else:
                    incorrect += 1

            # Тест нәтижесін жинақтау
            score = TestResult.objects.filter(student=student_user.login, test=test).first()

            submissions.append({
                "test": test,
                "score": score.score if score else 0,
                "correct": correct,
                "incorrect": incorrect,
                "total": len(student_answers),
                "questions": question_data,
            })

    context = {
        "class_model": class_model,
        "students": students,
        "selected_student": selected_student,
        "selected_student_id": selected_student_id,
        "status": status,
        "graded_student_ids": list(graded_student_ids),
        "submissions": submissions,
    }

    return render(request, "testwork.html", context)


def codework(request, class_id):
    class_model = get_object_or_404(ClassModel, id=class_id)
    students = Student.objects.filter(classmodel=class_model)
    
    status = request.GET.get("status", "all")
    graded_student_ids = Grade.objects.filter(
        student__in=students
    ).values_list('student__login__id', flat=True).distinct()

    if status == "graded":
        students = students.filter(login__id__in=graded_student_ids)
    elif status == "pending":
        students = students.exclude(login__id__in=graded_student_ids)

    selected_student_id = request.GET.get("student_id")
    selected_student = None
    latest_submission = None
    latest_task = None
    ktp = None

    if selected_student_id:
        selected_student = get_object_or_404(Student, id=selected_student_id)

        # Ең соңғы CodeTaskSubmission (үй жұмысы) осы оқушыдан
        latest_submission = CodeTaskSubmission.objects.filter(
            student=selected_student.login
        ).order_by('-submitted_at').first()

        if latest_submission:
            latest_task = latest_submission.task  # CodeTask
            ktp = latest_task.lesson  # Бұл — Ktp моделі

    context = {
        "class_model": class_model,
        "students": students,
        "selected_student": selected_student,
        "selected_student_id": selected_student_id,
        "status": status,
        "graded_student_ids": list(graded_student_ids),
        "latest_task": latest_task,
        "latest_submission": latest_submission,
        "ktp": ktp,  # Ktp мәліметін қосу
    }

    return render(request, "codework.html", context)







