from django.contrib import admin
from .models import Answer, ClassModel, CodeTask, CodeTaskSubmission, Lesson, Login, Question, StudentAnswer, StudentTestResult, TaskType, Teacher, Test, Testview, ThreeDModel, VideoLesson, VideoTest, WrittenTask, WrittenTaskSubmission
from .models import Student, Grade, Quarter, Ktp, Room, Course, ChatMessage, Profile, Friend, TestResult

admin.site.register(Login)
admin.site.register(Student)
admin.site.register(Grade)
admin.site.register(Quarter)
admin.site.register(Ktp)
admin.site.register(Room)
admin.site.register(Course)
admin.site.register(ChatMessage)
admin.site.register(Profile)
admin.site.register(Friend)
admin.site.register(ThreeDModel)
admin.site.register(Teacher)
admin.site.register(VideoLesson)
admin.site.register(VideoTest)
admin.site.register(Test)
admin.site.register(Lesson)
admin.site.register(StudentTestResult)
admin.site.register(TaskType)
admin.site.register(Testview)
admin.site.register(WrittenTask)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(CodeTask)
admin.site.register(StudentAnswer)
admin.site.register(TestResult)
admin.site.register(WrittenTaskSubmission)
admin.site.register(CodeTaskSubmission)
admin.site.register(ClassModel)





