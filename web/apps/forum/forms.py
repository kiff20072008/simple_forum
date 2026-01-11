from django import forms
from django_summernote.widgets import SummernoteWidget
from .models import News, NewsComment, Thread, ThreadPost

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content']
        widgets = {'content': SummernoteWidget()}

class NewsCommentForm(forms.ModelForm):
    class Meta:
        model = NewsComment
        fields = ['content']
        widgets = {'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})}

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title', 'content']
        widgets = {'content': SummernoteWidget()}

class PostForm(forms.ModelForm):
    class Meta:
        model = ThreadPost
        fields = ['content']
        widgets = {'content': SummernoteWidget()}