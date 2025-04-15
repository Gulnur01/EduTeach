from datetime import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

class ClassModel(models.Model):
    id = models.AutoField(primary_key=True)  # Автоинкрементируемый ID (по умолчанию)
    class_name = models.CharField(max_length=50)  # Поле для "class"
    option = models.CharField(max_length=50)     # Поле для "variant"
    teacher = models.CharField(max_length=100)  # Поле для "rukovoditel"
    number = models.CharField(max_length=15, blank=True, null=True)  # Поле для "number"

    def __str__(self):
        return f"{self.class_name} - {self.option} - {self.teacher}"
    
class Login(models.Model):
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)  # Убедитесь, что email уникален
    password = models.CharField(max_length=128)  # Храните пароль в виде хэшированной строки
    photo = models.ImageField(upload_to='static/img/', blank=True, null=True)  # Поле для изображения

    def __str__(self):
        return f"{self.user_name} - {self.last_name}"
    
class Student(models.Model):
    classmodel=models.ForeignKey(ClassModel, on_delete = models.CASCADE, related_name="students")
    login=models.ForeignKey(User, on_delete = models.CASCADE, related_name="login") 

    def __str__(self):
        return f"{self.login.first_name} {self.login.last_name}"
    
class Quarter(models.Model):
    classmodel = models.ForeignKey(ClassModel, on_delete=models.CASCADE, related_name='grades1')
    quarter=models.IntegerField()  # Поле для "number"
    tema=models.CharField(max_length=150)

    def __str__(self):
        return f"{self.tema }"
    
class Ktp(models.Model):
    quarter1 = models.ForeignKey(Quarter, on_delete=models.CASCADE, related_name='ktps')
    number=models.IntegerField()  # Поле для "number"
    tema=models.CharField(max_length=150)
    purpose=models.CharField(max_length=400)
    number_of_hours=models.IntegerField()  # Поле для "number"
    date=models.DateField()  # Баға қойылған күн
    homework=models.CharField(max_length=150)

    def __str__(self):
        return f"{self.tema}"    
      
    
class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    tema = models.ForeignKey(Ktp, on_delete=models.CASCADE)
    date = models.DateField()  # Баға қойылған күнpy
    grade = models.IntegerField()  # Баға

    def __str__(self):
        return f"{self.student.login.username} - {self.date}: {self.grade}"

        
class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name    
    
class Course(models.Model):  # Пример, если нужна связь учитель-студент через курсы
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_taught')
    students = models.ManyToManyField(User, related_name='courses_enrolled')

    def __str__(self):
        return self.name    
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    pic = models.ImageField(upload_to='static/img/', blank=True, null=True)
    friends = models.ManyToManyField('Friend', related_name = "my_friends")
    
    def __str__(self):
        return self.name
    
    
class Friend(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.profile.name

class ChatMessage(models.Model):
    body = models.TextField()
    msg_sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="msg_sender")
    msg_receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="msg_receiver")
    seen = models.BooleanField(default=False)
    
    def __str__(self):
        return self.body
    
class ThreeDModel(models.Model):
    name = models.CharField(max_length=255)
    description=models.TextField()
    image = models.ImageField(upload_to='static/img/')
    model_file = models.FileField(upload_to='models/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} {self.description}"
    
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    date_of_birth = models.DateField(verbose_name="Дата рождения", null=True, blank=True)
    gender_choices = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
    ]
    gender = models.CharField(max_length=1, choices=gender_choices, verbose_name="Пол", blank=True)
    phone_number = models.CharField(max_length=15, verbose_name="Телефон", blank=True)
    address = models.TextField(verbose_name="Адрес проживания", blank=True)
    
    # Профессиональная информация
    education_level = models.CharField(max_length=255, verbose_name="Уровень образования", blank=True)
    specialty = models.CharField(max_length=255, verbose_name="Специальность", blank=True)
    alma_mater = models.CharField(max_length=255, verbose_name="Учебное заведение", blank=True)
    diplomas_certificates = models.FileField(upload_to='models/', verbose_name="Дипломы и сертификаты", blank=True)
    work_experience_years = models.PositiveIntegerField(verbose_name="Стаж работы (в годах)", null=True, blank=True)
    subjects_taught = models.CharField(max_length=255, verbose_name="Преподаваемые предметы", blank=True)
    academic_title = models.CharField(max_length=255, verbose_name="Академическое звание или степень", blank=True)

    # Рабочие данные
    workplace = models.CharField(max_length=255, verbose_name="Место работы", blank=True)
    position = models.CharField(max_length=255, verbose_name="Должность", blank=True)
    rating = models.FloatField(verbose_name="Рейтинг или оценка", null=True, blank=True)
    awards = models.TextField(verbose_name="Награды и грамоты", blank=True)
    
    def __str__(self):
        return self.address   
    
class VideoLesson(models.Model):
    addlesson=models.ForeignKey(Ktp, on_delete=models.CASCADE, related_name='add')
    image = models.ImageField(upload_to='static/img/', default='static/img/ai.jpeg')
    description=models.TextField()
    video_file = models.FileField(upload_to='models/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(blank=True, null=True, help_text="Длительность в секундах")  # Продолжительность
    
class VideoTest(models.Model):
    lesson = models.ForeignKey(VideoLesson, related_name='tests', on_delete=models.CASCADE)
    timestamp = models.IntegerField(help_text="Время в секундах, когда появится тест")  # Время показа
    question = models.TextField()  # Вопрос
    correct_answer = models.CharField(max_length=200)  # Правильный ответ
    options = models.JSONField(default=list, help_text="Список вариантов ответа")  # Варианты ответа
    
class Lesson(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Test(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, default=1)
    questions = models.JSONField(default=dict)  # Формат: {question: [options], correct_answer: index}
    generated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Test for {self.lesson.name} - Generated at {self.generated_at}"

class StudentTestResult(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    answers = models.JSONField()  # Формат: {question_index: selected_option_index}
    analysis_report = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)    
    
class TaskType(models.Model):
    """Тапсырма түрі"""
    name = models.CharField(max_length=100)  # "Тест", "Жазбаша тапсырма", "Есеп"
    img=models.ImageField(upload_to='static/img/', blank=True, null=True)

    def __str__(self):
        return self.name    
    
class Testview(models.Model):
    lesson = models.ForeignKey(Ktp, on_delete=models.CASCADE)  # Много тестов для одного урока
    tasktype = models.ForeignKey(TaskType, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    test = models.ForeignKey(Testview, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=300)  # Текст вопроса

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    text = models.CharField(max_length=255)  # Текст ответа
    is_correct = models.BooleanField(default=False)  # Является ли правильным ответом
    
class StudentAnswer(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)    
    
class TestResult(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)  # Ученик
    test = models.ForeignKey(Testview, on_delete=models.CASCADE)  # Тест, который он прошел
    score = models.FloatField()  # Итоговый балл (в процентах)
    completed_at = models.DateTimeField(auto_now_add=True)  # Когда тест завершен    
    
class WrittenTask(models.Model):
    """ Жазбаша тапсырмалар """
    lesson = models.ForeignKey(Ktp, on_delete=models.CASCADE)  # Сабаққа байланысу
    tasktype = models.ForeignKey(TaskType, on_delete=models.CASCADE)
    text = models.TextField()  # Жазбаша тапсырма мәтіні
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Жазбаша тапсырма для {self.lesson.tema}"   
    
class CodeTask(models.Model):
    lesson = models.ForeignKey(Ktp, on_delete=models.CASCADE)
    tasktype = models.ForeignKey(TaskType, on_delete=models.CASCADE)
    description = models.TextField()  # Шарт (условие задачи)
    code = models.TextField()  # Код решения
    input_data = models.TextField(blank=True, null=True)  # Входные данные (если нужны)
    output = models.TextField()  # Вывод (результат выполнения)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Есеп: {self.description[:30]}..."  
    
class TestAttempt(models.Model):# қате
    """ Оқушының тест тапсыру нәтижесі """
    student = models.ForeignKey(User, on_delete=models.CASCADE)  # Оқушы
    test = models.ForeignKey(Testview, on_delete=models.CASCADE)  # Қандай тест
    completed_at = models.DateTimeField(auto_now_add=True)  # Аяқтау уақыты

    def __str__(self):
        return f"{self.student.username} - {self.test.lesson.tema}"

class TestAnswer(models.Model): # қате
    """ Оқушының тест сұрақтарына берген жауаптары """
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name="answers")  
    question = models.ForeignKey(Question, on_delete=models.CASCADE)  # Қандай сұрақ
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)  # Таңдалған жауап
    is_correct = models.BooleanField()  # Дұрыс па, жоқ па

    def __str__(self):
        return f"{self.attempt.student.username} - {self.question.text[:30]}..."


class WrittenTaskSubmission(models.Model):
    """ Жазбаша тапсырманың жауабы """
    student = models.ForeignKey(User, on_delete=models.CASCADE)  # Оқушы
    task = models.ForeignKey(WrittenTask, on_delete=models.CASCADE)  # Қай тапсырмаға жауап
    answer_text = models.TextField()  # Оқушының жазған жауабы
    submitted_at = models.DateTimeField(auto_now_add=True)  # Жіберілген уақыт
    graded = models.BooleanField(default=False)  # Бағаланған ба?

    def __str__(self):
        return f"{self.student.username} - {self.task.lesson.tema}"


class CodeTaskSubmission(models.Model):
    """ Есептің (код тапсырмасы) жауабы """
    student = models.ForeignKey(User, on_delete=models.CASCADE)  # Оқушы
    task = models.ForeignKey(CodeTask, on_delete=models.CASCADE)  # Қай есепке жауап
    submitted_code = models.TextField()  # Оқушының жазған коды
    submitted_at = models.DateTimeField(auto_now_add=True)  # Жіберілген уақыт
    is_correct = models.BooleanField(null=True, blank=True)  # Дұрыс па?

    def __str__(self):
        return f"{self.student.username} - {self.task.description[:30]}..."    
    
    
    
   
     
    
    
