# forms.py
from django import forms
from django.forms import ModelForm
from .models import ChatMessage, VideoLesson, VideoTest
from django import forms


class ChatMessageForm(ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={"class":"forms", "rows":3, "placeholder": "Type message here"}))
    class Meta:
        model = ChatMessage
        fields = ["body",]
        
class ImageUploadForm(forms.Form):
    image = forms.ImageField()      
    
class VideoLessonForm(forms.ModelForm):
    class Meta:
        model = VideoLesson
        fields = ['addlesson', 'description', 'video_file', 'duration']

class VideoTestForm(forms.ModelForm):
    class Meta:
        model = VideoTest
        fields = ['lesson', 'timestamp', 'question', 'correct_answer', 'options']
        
        